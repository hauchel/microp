import network
import time
import webrepl
class conn:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        #self.wlan.active(False)
    def an(self):
        self.wlan.active(True)
        print("conn.an, self.wlan",self.wlan.active())
        self.wlan.connect('FRITZ!HH','47114711')
        for i in range(10):
            print ("Wait Connect",i)
            if self.wlan.isconnected(): break
            time.sleep(1)
        webrepl.start()
        
    def aus(self):
        self.wlan.active(False)
        print("conn.aus, self.wlan",self.wlan.active())

#nw=conn()
#nw.an()
#print("conn.nw.an()")
