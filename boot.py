# Network depending on GPIO14
#
import sys
impl=sys.implementation[2].split()[-1]  # ESP8266 ESP32 
print('Running on',impl)
print("\x1b]2;"+impl+"\x07", end="") #Teraterm title change request
import esp
esp.osdebug(None)

from machine import Pin
p14 = Pin(14, Pin.IN, Pin.PULL_UP)
print("\nGPIO 14 ",p14.value())
from myconn import conn
nw=conn()
if p14.value()==1 :   
    nw.an()
else:
    print("\nGPIO 14 ",p14.value(),'No Connect!')
    nw.aus()
print("boot done")
