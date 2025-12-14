import network
import time
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('ESP32_AP','47114711')
for i in range(10):
    print ("Wait Connect",i)
    if wlan.isconnected():
        break
    time.sleep(1)
print(wlan.ifconfig())