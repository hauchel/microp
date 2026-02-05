# espnow Client            
# Vorsicht!               D1:
# RST                     RST
# ADC                     ADC
# EN                      GPIO16 !!!
# GPIO16  Wake zu RST     GPIO14 !!!
# GPIO14  Netwrk Start
# GPIO12
# GPIO13
# VCC                     3.3V
# Ablauf s.u.

import sys
import uselect
import machine 
import time
import gc
from espn import espn

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

pinSDA = machine.Pin(4)  # green
pinSCL = machine.Pin(5)  # yell  
i2c = machine.I2C(scl=pinSCL, sda=pinSDA)
print("encli Scanning...", end=' ')
devs=i2c.scan()
print(devs)

adcGain=1
adcRate=6
adcChan=0
if 72 in devs:
    from myADS1115 import ADS1115
    adc=ADS1115(i2c, address=72, gain=adcGain)
elif 75 in devs:
    from myADS1115 import ADS1115
    adc=ADS1115(i2c, address=75, gain=adcGain)
else: adc=None
if adc: adc.set_conv(rate=adcRate, channel1=adcChan)


cmd=''          # command received
nachricht=''    # to send
shotime=1000  # jede sekunde, set by T
shotick=0     # akt
showas=15     # 1/0 überhaupt, wenn nix anderes Spannung
shoraw=0      # 1 raw 
shotmp=0      # 1 Temp
showid=0      # 1 Widerst
shomed=0      # anzahl miwe
forw=True     # an Server
raws=[[], [], [], []]


from conf44 import CONF
cfg=CONF()

class xmenu:
    def __init__(self):
        self.inpAkt=False
        self.strmode=False
        self.inp=0
        self.stack=[]
        self.inpStr=''
        self.myip=33

    def prompt(self):
        self.strmode=False
        print (self.inp,end=">")
        return
        if self.myip !=0:
            print (self.myip,end=">")
        else:
            print ('??',end=">")
    
    def mach(self,ch):
        print(ch,end='')
        if self.strmode:
            if ch=='#':
                print()
                self.prompt()
            elif ch=='\b':
                self.inpStr=self.inpStr[:-1]
            elif ch=='\n':
                print(f">{self.inpStr}<")
                if self.inpStr =='':
                    self.prompt()
                else:
                    #myn.sende(inp, inpStr)
                    self.inpStr=''
                    print("'",end='')
            else:
                self.inpStr+=ch
            return  True
            
        if ((ch >= '0') and (ch <= '9')):
            if (self.inpAkt):
                self.inp = self.inp * 10 + (ord(ch) - 48)
            else:
                self.inpAkt = True
                self.inp = ord(ch) - 48
            return True
        self.inpAkt=False
        if  ch==",":
            self.stack.append(self.inp)
        elif ch=="+":
            self.inp=self.inp+self.stack.pop()
            print('=',self.inp)
        elif ch=="-":
            self.inp=self.stack.pop()-self.inp
            print('=',self.inp)
        elif ord(ch)==228:
            self.inpStr=''
            self.strmode=True
        else:
            return False
        return True
        
men=xmenu()

myn=espn()
print("Server is",myn.servip)
print("\x1b]2;"+"Cli "+str(myn.myip)+"\x07", end="") #Teraterm title change request


pidef= {2:1,4:0,5:0}    #default for outports
pins = {}
for p in pidef:
    pins[p]=machine.Pin(p, machine.Pin.OUT)
    pins[p].value(pidef[p])

def setpin(pi,va):
    print ("setpin",pi,va)
    if va==0:
        pins[pi].off()
    else:
        pins[pi].on()

def pinh(pi,du):
    print ("hpin",pi,du)
    if pidef[pi]==0:
        pins[pi].on()
    else:
        pins[pi].off()
    time.sleep_ms(du)
    pins[pi].value(pidef[pi])

def deepsl(ms):
    print("Deepsl",ms)
    if myn.is32:
        from machine import deepsleep
        deepsleep(ms)
    # 8266, connect GPIO16 to the reset pin
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire 
    rtc.alarm(rtc.ALARM0, ms)
    # put the device to sleep
    machine.deepsleep()    
    print("Hä?")
 
def lightsl(ms):
    # 8266: 0 NONE, 1 LIGHT 2 MODEM
    myn.wlan.active(False)
    print("Light",myn.wlan.active()) 
    machine.lightsleep(ms)
    myn.wlan.active(True)
    
   
def adcInfo():
    print("Gain",adcGain,"Rate", adcRate,"Chan",adcChan)

def raw_to_r(raw, chan):    
    uin=adc.raw_to_v(raw)
    if uin < 3.01: 
        return int(cfg.rtop[chan]*uin/(cfg.vcc-uin))
    else:
        return 99999   # offener eingang

def evalmed():
    print("ata:")
    for n in range(4):
        if len(raws[n])>0:
            mi=min(raws[n])
            ma=max(raws[n])
            di=ma-mi
            print(f"{n} {di:3}  {mi:5}  {ma:5} ",raws[n])     
         
def show():
    tx=""
    for n in range(4):
        if showas & (1 << n):
            raw=adc.read(rate=adcRate, channel1=n)  
            if shomed > 0:
                raws[n].append(raw)
                if len(raws[n])>shomed:
                    raws[n].pop(0)
            druv=True       #voltage nur wenn nix anderes
            if shoraw  & (1 << n):
                tx+=f"{n}D: {raw:5}  "
                druv=False
            if showid  & (1 << n):
                tx+=f"{n}R: {raw_to_r(raw,n):5}  " 
                druv=False
            if shotmp  & (1 << n):
                tx+=f"{n}T: {cfg.temp(raw_to_r(raw,n),n):4.2f}  "
                druv=False                
            if druv:
                tx+=f"{n}V: {adc.raw_to_v(raw):3.3f}  "
    print("\b\b\b"+tx)   
    if forw:    
        myn.sende(myn.servip, tx)  
    
def hilf():
    print("""
    a       read current adc     
      ..c     channel
      ..g     gain
      ..p     rate
    t       dauer mit 
      ..T     tick in ms 
      ..z     1,2,4,8 zeigt chan 0 1 2 3
      ..y             raw
      ..w             Widerstand 
      ..x             Temp 
      ..D     Grösse med
    
    d       evalmed
    ..E     enow.active 0/1
    ..F     wlan.active 0/1
    ..f     forw active 0/1
    #,..h   set # to 1 for .. ms
    
    i       Info  
    m       Macs
    ..n     lightsl ..sec
    ..N     deepsl  ..sec
    r       recv
    ..s     send to ..
    ..v     verbose 
    ä       string mode, send to serv after CR
    #       terminate string mode
    """)

def cmdin():
    global cmd
    txt=input('cmd: ')
    cmd+=txt
    print(cmd)
    
def menu(ch):   
    global adcGain, adcRate, adcChan
    global shotime, showas, shotick, shoraw,showid,shotmp,shomed
    global raws
    global nachricht,forw

    try:
        if men.mach(ch): return False
        if ch=="a":         #
            raw=adc.read(rate=adcRate, channel1=adcChan)
            nachricht=f"{raw} = {adc.raw_to_v(raw):4.4f}V"
            print(nachricht)
        elif ch=="c": 
            adcChan=men.inp
            adc.set_conv(rate=adcRate, channel1=adcChan)
            adcInfo()         
        elif ch=="D": 
            shomed=men.inp
            print("Shomed",shomed)         
        elif ch=="d":      
            evalmed()            
        elif ch=="E":
            myn.e.active(men.inp!=0)
            print("ective",myn.e.active()) 
        elif ch=="f":
            forw= men.inp!=0
            print("forw",forw)             
        elif ch=="F":
            myn.wlan.active(men.inp!=0)
            print("wlan",myn.wlan.active())             
        elif ch=="g": 
            adcGain=men.inp
            adc.gain=adcGain
            adcInfo()                  
        elif ch=="h":
            pinh(men.stack[-1],men.inp)                
        elif ch=="i":
            myn.laninfo()       
            print(myn.lastipn,myn.lasttxt)         
            print(f"Alloc {gc.mem_alloc()}",end=" > ")
            gc.collect()
            print(f"Alloc {gc.mem_alloc()}  Free {gc.mem_free()}")
        elif ch=="m":
            print()
            myn.showmacs() 
        elif ch=="n":                
            lightsl(men.inp*1000)    
        elif ch=="N":                
            deepsl(men.inp*1000)   
        elif ch=="p": 
            adcRate=men.inp
            adc.set_conv(rate=adcRate, channel1=adcChan)
            adcInfo()                 
        elif ch=="q" or ch == '\x04':       # quit
            print ("restart with ",__name__+".loop() ")
            return True
        elif ch=="p":
            setpin(men.stack[-1],men.inp)
        elif ch=="r":
            myn.again()    
        elif ch=="s":
            myn.sende(men.inp, nachricht)    
        elif ch=="t":
            if shotick==0:
                shotick=shotime
                raws=[[], [], [], []]
                print()
                return False
            else:
                shotick=0 
        elif ch=="T":
                shotime=men.inp    
                print("Shotime",shotime)                    
        elif ch=="v":       
            myn.verbo = not myn.verbo
            print("verbo", myn.verbo)   
 
        elif ch=="w":
            showid=men.inp
            print("showid", showid,':') 
            show()         
        elif ch=="W":      #w,n aber 
            tmp=men.stack.pop()
            men.stack.append(tmp)
            cfg.rtop[tmp]=men.inp
            cfg.show()                  
        elif ch=="x":
            shotmp=men.inp
            print("shotmp", shotmp,':') 
            show()                                 
        elif ch=="y":
            shoraw=men.inp
            print("shoraw", shoraw,':') 
            show()                                        
        elif ch=="z":
            showas=men.inp
            print("show", showas,':') 
            show()               
        else:
            print("ord=",ord(ch))
            hilf()
    except Exception as inst:
        # print ("Menu",end=' ')        
        sys.print_exception(inst) 
    men.prompt()
    return False

def loop():
    global cmd
    tim=time.ticks_ms()
    lastsho=tim
    men.prompt()
    while True:
        try:
            if len(cmd) !=0:
                ch=cmd[0]
                cmd=cmd[1:]
                if menu(ch): break    
            if myn.e.any():
                cmd+=myn.reccli()
                if myn.verbo: print('>'+cmd+'<')
            if poller.poll(0):
                ch=sys.stdin.read(1)
                if menu(ch): break
            tim=time.ticks_ms()       
            if shotick > 0:
                difftick = time.ticks_diff(tim, lastsho)
                if difftick > shotick:
                    lastsho = tim
                    show()
 
        except Exception as inst:
            #print ("Loop",end=' ')
            sys.print_exception(inst)   
"""
# Ablauf:
# Wakeup  Netz inaktiv 
# Sammle
print("Sammle..")
time.sleep(3)
# espnow an
myn.wlan.active(True)
print("wlan",myn.wlan.active())  
myn.e.active(True)
print("ective",myn.e.active())  
# Schicke Daten an Server
if myn.sende(myn.servip, "Alle meine Entchen"):
# falls da warte etwas
    print("Succ")
else:
    print("Fail")       
"""    
loop()