# This file is executed on every boot (including wake-boot from deepsleep)
print(chr(27)+'c')
import esp
esp.osdebug(None)
#from machine import UART
#uart = UART(0, 38400) 
#print('\x1bc')      #reset terminal
import network
import time
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
import tstep





