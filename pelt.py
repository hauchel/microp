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
ticktime=0     #
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

def hilf():
    print("""
    ..a     
    ..e
    ..k     Kennlinie Step .. params von read_rev
    ..t     ticktime
    ..T     tick macht 0 1 2 3
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
    """)

def prompt():
    print ('??',end=">")
    
def adcInfo():
    print("Gain",adcGain,"Rate", adcRate,"Chan",adcChan)
    
def adcZeig():
    voltage0 = adc.read(rate=adcRate, channel1=0)
    voltage1 = adc.read(rate=adcRate, channel1=1)
    voltage2 = adc.read(rate=adcRate, channel1=2)
    voltage3 = adc.read(rate=adcRate, channel1=3)
    print("0: {:<8} 1: {:<8} 2: {:<8} 3: {:<8}".format(voltage0, voltage1, voltage2, voltage3))
    
def menu(ch):   
    global inpStr        
    global inpAkt
    global inp
    global stack
    global ticktime
    global verbo
    global adcGain
    global adcRate
    global adcChan
    try:
        print(ch,end='')            
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt):
                inp = inp * 10 + (ord(ch) - 48)
            else:
                inpAkt = True
                inp = ord(ch) - 48
            return
        else:
            inpAkt=False
            if ch == "b":  # scan (only from 0x08 to 0x77)
                print("\bScanning...", end=' ')
                print(i2c.scan())
            elif ch=="d":      
                print(adc.read_rev())
            elif ch=="a":      
                print(adc.read(rate=adcRate, channel1=adcChan))                
            elif ch=="c": 
                adcChan=inp
                adc.set_conv(rate=adcRate, channel1=adcChan)
                adcInfo()
            elif ch=="g": 
                adcGain=inp
                adc.gain=adcGain
                adcInfo()   
            elif ch=="i": 
                print(ina.read_current())
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
                ticktime=inp
                print("tick ms", ticktime)   
            elif ch=="u": 
                print(ina.read_voltage())
                
            elif ch=="v":       
                verbo = not verbo
                print("verbo", verbo)  
            elif ch=="z":
                adcZeig()   
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
    lasttick=time.ticks_ms()
    while True:
        try:
            if poller.poll(0):
                ch=sys.stdin.read(1)
                if menu(ch): break
            if ticktime > 0:
                difftick = time.ticks_diff(time.ticks_ms(), lasttick)
                if difftick > ticktime:
                    lasttick = time.ticks_ms()
                    adcZeig()

        except Exception as inst:
            #print ("Loop",end=' ')
            sys.print_exception(inst)   
prompt()                
loop()