import network
import time
print('Configure AP')
#der Name des Access Point
ssid = 'ESP32'
#das Passwort des Access Point
passwort = '47114711'
ap = network.WLAN(network.WLAN.IF_AP)
ap.config(essid=ssid, password=passwort)
ap.active(True)