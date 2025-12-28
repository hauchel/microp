# Network depending on GPIO14
#
import sys
impl=sys.implementation[2].split()[-1]  #ESP32 
print('Running on',impl)
print("\x1b]2;"+impl+"\x07", end="") #Teraterm title change request
import esp
esp.osdebug(None)

from machine import Pin
p14 = Pin(14, Pin.IN, Pin.PULL_UP)
print("\nGPIO 14 ",p14.value())
import network
import time

if p14.value()==0 :   
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('FRITZ!HH','47114711')
    #wlan.connect('NETGEAR','12345678')
    hots=network.WLAN(network.AP_IF)
    hots.active(False)
    for i in range(10):
        print ("Wait Connect",i)
        if wlan.isconnected():
            break
        time.sleep(1)
    import webrepl
    webrepl.start()
else:
    print("\nGPIO 14 ",p14.value(),'No Connect!')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
print("boot done")
