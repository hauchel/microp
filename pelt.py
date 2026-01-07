# Auswerten Pelztier
# Gpios:
# 5 (SCL)
# 4 (SDA)
# 72 adc  ADS1115
# 96 dac  MCP4725
# 64      INA219
import sys
import uselect
import time
import gc
from math import log
from machine import I2C,Pin

impl=sys.implementation[2].split()[-1]  #ESP32 ESP32C3 ESP8266
print('Howdy, Running on',impl)

# some globals    
start = time.ticks_ms()
if impl=='ESP32C3':
    pinSDA = Pin(8)  # green
    pinSCL = Pin(9)  # yell
else:
    pinSDA = Pin(4)  # green
    pinSCL = Pin(5)  # yell
    
i2c = I2C(scl=pinSCL, sda=pinSDA)

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

inpAkt=False
inpStr=''
inp=0
stack=[]
shotime=1000  # jede sekunde, set by Z
shotick=0     # akt
showas=15     # 1/0 überhaupt, wenn nix anderes Spannung
shoraw=0      # 1 raw 
shotmp=0      # 1 Temp
showid=0      # 1 Widerst

verbo=False

from myMCP4725 import MCP4725
dac=MCP4725(i2c,96)

from myADS1115 import ADS1115
adcGain=1
adcRate=4
adcChan=0
adc=ADS1115(i2c, address=72, gain=adcGain)
adc.set_conv(rate=adcRate, channel1=adcChan)

from myINA219 import INA219
ina=INA219(i2c)

from myKR import KENNL,REGL      
ken=KENNL(dac)               
reg=REGL()

from myCONF import CONF
cfg=CONF()         

def prompt():
    print ('>',end="")
    
def adcInfo():
    print("Gain",adcGain,"Rate", adcRate,"Chan",adcChan)

def inaZeig():
    print(f"U={ina.read_voltage():2.3f} I={ina.read_current():2.3f}")

def raw_to_r(raw, chan):    
    uin=adc.raw_to_v(raw)
    return int(cfg.rtop[chan]*uin/(cfg.vcc-uin))
        
def raw_to_t(raw,chan):
    T0=298.15
    rntc=raw_to_r(raw,chan)
    tempk = 1 / ((1/T0) + cfg.betar[chan] * log(rntc / cfg.rntc0[chan]))
    return tempk - 273.15

def show():
    tx="\b\b\b"
    for n in range(4):
        if showas & (1 << n):
            raw=adc.read(rate=adcRate, channel1=n)   
            druv=True       #voltage nur wenn nix anderes
            if shoraw  & (1 << n):
                tx+=f"{n}D: {raw:5}  "
                druv=False
            if showid  & (1 << n):
                tx+=f"{n}R: {raw_to_r(raw,n):5}  " 
                druv=False
            if shotmp  & (1 << n):
                tx+=f"{n}T: {raw_to_t(raw,n):4.2f}  "
                druv=False                
            if druv:
                tx+=f"{n}V: {adc.raw_to_v(raw):3.3f}  "
    print(tx,end=' ')
    if showas & (1 << 4):
        print(f"U={ina.read_voltage():2.3f} I={ina.read_current():2.3f}")
    else:
        print()

def info():
    print(f"Alloc {gc.mem_alloc()}",end=" > ")
    gc.collect()
    print(f"Alloc {gc.mem_alloc()}  Free {gc.mem_free()}")
    print("T",shotime," Z",showas," X",shotmp," Y",shoraw," W",showid)
    
def menu(ch):   
    global inpStr,inpAkt,inp, stack
    global shotime, showas, shotick, shoraw,showid,shotmp
    global verbo
    global adcGain, adcRate, adcChan
    try:         
        if ((ch >= '0') and (ch <= '9')):
            print(ch,end='')   
            if (inpAkt):
                inp = inp * 10 + (ord(ch) - 48)
            else:
                inpAkt = True
                inp = ord(ch) - 48
            return False# kein prompt
        else:
            print(ch,end=' ')            
            inpAkt=False
            if ch == "b": 
                print("Scanning...", end=' ')
                print(i2c.scan())
            elif ch==" ":  #Nothalt
                reg.stop()
                dac.set_value(0)
                ken.tick=0
                shotick=0
            elif ch=="a":      
                print(adc.read(rate=adcRate, channel1=adcChan))                
            elif ch=="A":      
                ken.klA=inp
                ken.parms()
            elif ch=="B":   
                tmp=stack.pop()
                stack.append(tmp)
                cfg.betar[inp]=1.0/tmp
                cfg.show()                
            elif ch=="c": 
                adcChan=inp
                adc.set_conv(rate=adcRate, channel1=adcChan)
                adcInfo()
            elif ch=="d":      
                print(adc.read_rev())
            elif ch=="D":      
                ken.klD=inp
                ken.parms()
            elif ch=="E":      
                ken.klE=inp
                ken.parms()                
            elif ch=="g": 
                adcGain=inp
                adc.gain=adcGain
                adcInfo()   
            elif ch=="i": 
                print(f"{ina.read_current():2.3f}")
            elif ch=="j": 
                info()
                cfg.show()
            elif ch=="k":
                ken.anfang()
                print("...")
                return
            elif ch=="K":      
                ken.klK=inp
                ken.parms()
            elif ch=="N":      
                ken.klN=inp
                ken.parms()   
            elif ch=="M":      #w,n aber 
                tmp=stack.pop()
                stack.append(tmp)
                cfg.rtop[inp]=tmp
                cfg.show()
            elif ch=="o":      
                dac.set_value(inp)
                print ("dac" ,inp)
            elif ch=="q" or ch == '\x04':       # quit
                print ("restart with ",__name__+".loop() ")
                return True
            elif ch=="r":      
                reg.start(inp)
            elif ch=="R":      
                reg.tiset=inp
                reg.info()     
            elif ch=="s":      
                stell=reg.regel(ina.read_current())
                print("Stell",stell)
                dac.set_value(stell)                   
            elif ch=="S":      
                reg.sayset=inp
                reg.say==inp
                reg.info()     
            elif ch=="t":
                if shotick==0:
                    shotick=shotime
                    print()
                    return False
                else:
                    shotick=0
            elif ch=="T":
                shotime=inp    
                print("Shotime",inp)                 
            elif ch=="u": 
                print(f"{ina.read_voltage():2.3f}")                
            elif ch=="v":       
                verbo = not verbo
                print("verbo", verbo)  
            elif ch=="V":      
                cfg.vcc=inp
                cfg.show()      
            elif ch=="W":
                showid=inp
                print("showid", showid,':') 
                show()   
            elif ch=="x": 
                adcRate=inp
                adc.set_conv(rate=adcRate, channel1=adcChan)
                adcInfo()                    
            elif ch=="X":
                shotmp=inp
                print("shotmp", shotmp,':') 
                show()                                 
            elif ch=="Y":
                shoraw=inp
                print("shoraw", shoraw,':') 
                show()                      
            elif ch=="z":
                show()                   
            elif ch=="Z":
                showas=inp
                print("show", showas,':') 
                show()                     
            elif ch==",":
                stack.append(inp)
                return
            elif ch==".":
                inp=stack.pop()
                print('=',inp)
                return False
            elif ch=="+":
                inp=inp+stack.pop()
                print('=',inp)
                return False
            elif ch=="-":
                inp=stack.pop()-inp
                print('=',inp)
                return False
            elif ch=="~":
                tmp=stack.pop()
                stack.append(inp)
                inp=tmp
                print('=',inp)
                return False                
            else:
                print("ord=",ord(ch),"?")
                cfg.hilf()
    except Exception as inst:
        print ("Menu",end=' ')        
        sys.print_exception(inst) 
    prompt()
    return False

def loop():
    global cmd
    tim=time.ticks_ms()
    lastsho=tim
    lastken=tim
    lastreg=tim
    
    while True:
        try:
            if poller.poll(0):
                ch=sys.stdin.read(1)
                if menu(ch): break
            tim=time.ticks_ms()
            if reg.tick >0:  #Regler first
                difftick = time.ticks_diff(tim, lastreg)
                if difftick > reg.tick:
                    lastreg = tim
                    dac.set_value(reg.regel(ina.read_current()))              
            if shotick > 0:
                difftick = time.ticks_diff(tim, lastsho)
                if difftick > shotick:
                    lastsho = tim
                    show()
            if ken.tick >0:
                difftick = time.ticks_diff(tim, lastken)
                if difftick > ken.tick:
                    lastken = tim
                    ken.store([ina.read_current(),ina.read_voltage()])                
        except Exception as inst:
            print ("Loop",end=' ')
            sys.print_exception(inst)   
prompt()                
loop()