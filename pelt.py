# Auswerten Pelztier
# Gpios:
# 5 (SCL)
# 4 (SDA)
# 72 adc  ADS1115
# 96 dac  MCP4725
#         INA219
import sys
import uselect
import time
import gc
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
showtime=0     #
showas=0
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

class KENNL:
    def __init__(self,dac):
        self.klA=0     # Anfang
        self.klD=20    # Delta
        self.klE=0     # am Ende
        self.klN=10    # Anzahl
        self.klNum=0   # akt
        self.klOut=0     # akt
        self.klK=100   # Ticktime
        self.klTick=0  # akt
        self.klV=False
        self.klData={}
        self.dac=dac
        self.parms()
    
    def anfang(self):
        self.klOut=self.klA
        self.klData={} 
        self.setz()
        self.klTick=self.klK
        self.klNum=0
        self.parms()
        
    def setz(self):
        self.dac.set_value(self.klOut)
        
    def schoen(self,val):
        if isinstance(val, int):
            return f"{val:>5}"
        elif isinstance(val, float):
            return f"{val:3.3f}"
        else:
            return str(val)

    def store(self,val):
        if self.klV:
            print(f"{self.klNum:>3} {self.klOut:>5} with {self.schoen(val)}")
        self.klData[self.klOut]=val
        self.klNum+=1
        if self.klNum>self.klN:
            self.klOut=self.klE
            self.klTick=0
            self.zeig()
        else:
            self.klOut+=self.klD
        self.setz()
        
    def parms(self):
        print(f"A={self.klA} D={self.klD} E={self.klE} N={self.klN} K={self.klK} V={self.klV} out={self.klOut}")
        
    def zeig(self):
        for key, val in self.klData.items():
            print(f"{key:>5} {self.schoen(val)}")
        
        
ken=KENNL(dac)       

def hilf():
    print("""
    ..a     
    ..e
   
    ..t     showtime
    ..T     1,2,4,8 zeigt chan 0 1 2 3
  dac    
    ..o     out dac 0..4095
  ina
    i       Strom
    u       Spannung
  adc
    ..c     Channel 0..3 4..7
    ..g     Gain 0=2/3*,1=1*,2=2*,3=4*,4=8*, 5=16*
    ..r     Rate 0..7
    a       read
    d       read_rev (!)
    z       zeig
 ..k     Kennlinie fuer o
    ..A      Anfangswert
    ..D      Delta
    ..N      Anzahl
    ..K      kltime in ms
    
    """)

def prompt():
    print ('>',end="")
    
def adcInfo():
    print("Gain",adcGain,"Rate", adcRate,"Chan",adcChan)
    
def adcZeig():
    voltage0 = adc.read(rate=adcRate, channel1=0)
    voltage1 = adc.read(rate=adcRate, channel1=1)
    voltage2 = adc.read(rate=adcRate, channel1=2)
    voltage3 = adc.read(rate=adcRate, channel1=3)
    print("0: {:<8} 1: {:<8} 2: {:<8} 3: {:<8}".format(voltage0, voltage1, voltage2, voltage3))

def inaZeig():
    print(f"U={ina.read_voltage():2.3f} I={ina.read_current():2.3f}")
    
    
def show():
    for n in range(4):
        if showas & (1 << n):
            print(f"{n}:{adc.read(rate=adcRate, channel1=n):>6}",end="  ")  
    print(f"U={ina.read_voltage():2.3f} I={ina.read_current():2.3f}")


    
def menu(ch):   
    global inpStr,inpAkt,inp, stack
    global showtime, showas
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
            return # kein prompt
        else:
            print(ch,end=' ')            
            inpAkt=False
            if ch == "b":  # scan (only from 0x08 to 0x77)
                print("\bScanning...", end=' ')
                print(i2c.scan())
            elif ch=="a":      
                print(adc.read(rate=adcRate, channel1=adcChan))                
            elif ch=="A":      
                ken.klA=inp
                ken.parms()
            elif ch=="D":      
                ken.klD=inp
                ken.parms()
            elif ch=="E":      
                ken.klE=inp
                ken.parms()                
            elif ch=="N":      
                ken.klN=inp
                ken.parms()
            elif ch=="K":      
                ken.klK=inp
                ken.parms()
            elif ch=="V":      
                ken.klV=(inp != 0)
                ken.parms()                
            elif ch=="c": 
                adcChan=inp
                adc.set_conv(rate=adcRate, channel1=adcChan)
                adcInfo()
            elif ch=="d":      
                print(adc.read_rev())
            elif ch=="g": 
                adcGain=inp
                adc.gain=adcGain
                adcInfo()   
            elif ch=="i": 
                print(f"{ina.read_current():2.3f}")
            elif ch=="k":
                ken.anfang()
                print("...")
                return
            elif ch=="r": 
                adcRate=inp
                adc.set_conv(rate=adcRate, channel1=adcChan)
                adcInfo()                
            elif ch=="o":      
                dac.set_value(inp)
                print ("dac" ,inp)
            elif ch=="q" or ch == '\x04':       # quit
                print ("restart with ",__name__+".loop() ")
                return True
            elif ch=="t":
                showtime=inp
                print("tick ms", showtime)   
            elif ch=="T":
                showas=inp
                print("show", showas,':') 
                show()                   
            elif ch=="u": 
                print(f"{ina.read_voltage():2.3f}")
                
            elif ch=="v":       
                verbo = not verbo
                print("verbo", verbo)  
            elif ch=="z":
                show()   
            elif ch==",":
                stack.append(inp)
                return
            elif ch=="+":
                inp=inp+stack.pop()
                print('=',inp)
                return
            elif ch=="-":
                inp=stack.pop()-inp
                print('=',inp)
                return
            else:
                print("ord=",ord(ch))
                hilf()
    except Exception as inst:
        # print ("Menu",end=' ')        
        sys.print_exception(inst) 
    prompt()
    return False

def loop():
    global cmd
    lastshow=time.ticks_ms()
    lastkl=lastshow
    while True:
        try:
            if poller.poll(0):
                ch=sys.stdin.read(1)
                if menu(ch): break
            tim=time.ticks_ms()
            if showtime > 0:
                difftick = time.ticks_diff(tim, lastshow)
                if difftick > showtime:
                    lastshow = tim
                    show()
            if ken.klTick >0:
                difftick = time.ticks_diff(tim, lastkl)
                if difftick > ken.klTick:
                    lastkl = tim
                    ken.store(ina.read_current())                
        except Exception as inst:
            #print ("Loop",end=' ')
            sys.print_exception(inst)   
prompt()                
loop()