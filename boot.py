# This file is executed on every boot (including wake-boot from deepsleep)
print(chr(27)+'c')
import esp
from machine import Pin
import network
import time
esp.osdebug(None)
# check 14 (next to wake)
p14 = Pin(14, Pin.IN, Pin.PULL_UP)
print("\nGPIO 14 ",p14.value())
wlan = network.WLAN(network.STA_IF)
if p14.value()==1:   
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
    wlan.active(False)
    print("\nGPIO 14 ",p14.value(),'No Network!')
    time.sleep(2)
print("boot done")





