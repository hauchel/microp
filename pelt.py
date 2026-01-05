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
        self.klA=1500     # out Anfang
        self.klD=50    # Delta
        self.klE=0     # out am Ende
        self.klN=20    # Anzahl
        self.klNum=0   # akt N
        self.klOut=0   # akt O
        self.klK=10    # Ticktime
        self.tick=0    # akt
        self.klV=0
        self.klData={}
        self.dac=dac
        self.parms()
    
    def anfang(self):
        self.klOut=self.klA
        self.klData={} 
        self.setz()
        self.tick=self.klK
        self.klNum=0
        self.parms()
        
    def setz(self):
        self.dac.set_value(self.klOut)
        
    def schoen(self,val):
        if isinstance(val, int):
            return f"{val:>5}"
        elif isinstance(val, float):
            return f"{val:3.3f}"
        elif isinstance(val, list):
            tmp=""
            for w in val:
                tmp=tmp+self.schoen(w)+"  "
            return tmp
        else:
            return str(val)

    def store(self,val):
        if self.klV:
            print(f"{self.klNum:>3} {self.klOut:>5} with {self.schoen(val)}")
        self.klData[self.klOut]=val
        self.klNum+=1
        if self.klNum>self.klN:
            self.klOut=self.klE
            self.tick=0
            self.zeig()
        else:
            self.klOut+=self.klD
        self.setz()
        
    def parms(self):
        print(f"A={self.klA} D={self.klD} E={self.klE} N={self.klN} K={self.klK} V={self.klV} out={self.klOut}")
        
    def zeig(self):
        for key in sorted(self.klData):
            print(f"{key:>5} {self.schoen(self.klData[key])}")
        
       
ken=KENNL(dac)       

class REGL:
    def __init__(self):
        # Strom in A:
        self.soll=0 
        self.abwd=[-0.1, -0.05, +0.05, +0.1]
        self.sted=[ -10  , -2  ,   0,   +2,   +10] # wenn < abwd dieses sted
        self.stetop=len(self.sted)-1     # zeigt auf grösstes sted
        # Stellwert 0 .. 4095
        self.stell=0
        self.stellMin=0
        self.stellMax=4095
        self.tiset=100    # Tick ms
        self.tick=0       # akt
        self.sayset=10    # nach n Ausgabe
        self.say=0        # akt
    
    def start(self,soll): # in mA
        self.soll=soll/1000.0
        self.tick=self.tiset
        self.say=1
        print(f"Soll {self.soll:2.3f} tick {self.tick} say{self.sayset}")

    def stop(self):
        self.tick=0
        print("stop")

    def regel(self,ist):
        self.abw=self.soll - ist
        stedneu=self.sted[self.stetop]
        for n in range(self.stetop):
            if self.abw < self.abwd[n]: 
                stedneu =self.sted[n]
                break
        self.stell+=stedneu
        if self.stell < self.stellMin:
            self.stell=self.stellMin
        elif self.stell > self.stellMax:
            self.stell=self.stellMax      
        #print (self.say,time.ticks_ms())
        if self.say >0:
            if self.say == 1:
                print(f"Ist {ist:2.3f}  Abw {self.abw:2.3f}  Delt {stedneu} ->Stell {self.stell}")
                self.say=self.sayset
            else:
                self.say -=1
        return self.stell

    def info(self):
        print("Soll",self.soll,"Soll",self.soll,"Tick ",self.tiset,"Akt",self.tick,"Say",self.sayset)
        
reg=REGL()


def hilf():
    print("""
    b       i2c scan
    j       info   
    ..t     showtime in ms
    ..T     1,2,4,8 zeigt chan 0 1 2 3
 ina:
    i       Strom
    u       Spannung
 adc:
    ..c     Channel 0..3 4..7
    ..g     Gain 0=2/3*,1=1*,2=2*,3=4*,4=8*, 5=16*
    ..x     Rate 0..7
    a       read
    d       read_rev (!)
    z       zeig
 dac:    
    ..o     out dac 0..4095    
    ..k     Kennlinie fuer o
    ..A      Anfangswert
    ..D      Delta
    ..N      Anzahl
    ..E      Endwert wenn ferdisch
    ..K      ticktime in ms
    ..V      verbose 0/1
 reg:
    ..r      regel auf soll ..
    ..R      ticktime in ms
    ..S      Ausgabe nach .. Regelungen
    s        single step
 
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

def info():
    print(f"Alloc {gc.mem_alloc()}",end=" > ")
    gc.collect()
    print(f"Alloc {gc.mem_alloc()}  Free {gc.mem_free()}")

    
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
                showtime=0
            elif ch=="a":      
                print(adc.read(rate=adcRate, channel1=adcChan))                
            elif ch=="A":      
                ken.klA=inp
                ken.parms()
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
            elif ch=="V":      
                ken.klV=inp
                ken.parms()      
            elif ch=="x": 
                adcRate=inp
                adc.set_conv(rate=adcRate, channel1=adcChan)
                adcInfo()                    
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
                return False
            else:
                print("ord=",ord(ch))
                hilf()
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
            if showtime > 0:
                difftick = time.ticks_diff(tim, lastsho)
                if difftick > showtime:
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