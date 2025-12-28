import network

sta = network.WLAN(network.STA_IF)
sta.active(False)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32_AP", password="12345678")

print("AP ready:", ap.ifconfig())
