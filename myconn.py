import sys
import network
import time
import uselect
import webrepl
class conn:
    def __init__(self):
        self.ap=network.WLAN(network.WLAN.IF_AP)
        if self.ap.active(): self.ap.active(False)   #somehow it remembers status of previous settings
        self.sta = network.WLAN(network.WLAN.IF_STA)
        
    def an(self):
        self.sta.active(True)
        print("conn.an, self.sta",self.sta.active())
        self.sta.connect('FRITZ!HH','47114711')                 
        poller = uselect.poll()
        poller.register(sys.stdin, uselect.POLLIN)
        for i in range(10):
            print ("Wait Connect",i)
            if self.sta.isconnected(): break
            if poller.poll(0):
                ch=sys.stdin.read(1)
                return
            time.sleep(1)
        webrepl.start()
        
    def aus(self):
        self.sta.active(False)
        print("conn.aus, self.sta",self.sta.active())

#nw=conn()
#nw.an()
#print("conn.nw.an()")
