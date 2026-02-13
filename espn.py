import sys
import time
import network
import espnow
import ubinascii

class espn():
    # Mnn, Ann
    # broadcasts esp8266
    #   send: don't add to peer
    #   receive: von 32: geht nicht 
    # unbedingt connection zu fritzbox disablen!
    def __init__(self,waktiv=True):
        self.is32 = (sys.platform == 'esp32')
        
        self.macs = { 29: b'\xE8\xDB\x84\xC5\x1E\x3D', 31: b'\xc8\xc9\xa3\xc5\xfe\xfc', 
                      41: b'\xE8\xDB\x84\xDF\x94\x78', 43: b'\xE8\xDB\x84\xC5\x3C\xA7', 44: b'\xe8\xdb\x84\xc6\x2d\x7a', 45: b'\xe8\xdb\x84\xdf\x4d\x30',
                      48: b'\xe8\xdb\x84\xc5\xeb\x88',
                      53: b'\xd8\xbf\xc0\r\xea\x0c',   55: b'\x84\xF3\xEB\x0D\x71\x9E', 56: b'\xe0\x98\x06\x21\xb0\x2e' }
        self.servip=56
        if self.is32: self.macs[0]=b'\xFF\xFF\xFF\xFF\xFF\xFF' #broadcast
        self.ips={}
        for m in self.macs:
            self.ips[self.macs[m]]=m
        self.mychan=1
        self.wlan = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
        self.wlan.active(waktiv)
        self.mymac=self.wlan.config('mac')
     
        try:
            self.myip=self.ips[self.mymac] # bei key error in macs aufnehmen
            print("me",self.macz(self.mymac),self.myip)  
        except:
            print (self.macz(self.mymac),'not in self.macs',end=': ')
            self.macbin(self.mymac)
            self.myip = 0
        self.wlan.disconnect()      # MUSS für gute Übertragung
        self.e = espnow.ESPNow()
        self.e.active(waktiv)
        for ip in self.macs:
            #print(ip,self.macz(self.macs[ip]))
            if ip != self.myip:
                self.e.add_peer(self.macs[ip])
#            if self.is32:
#                self.e.add_peer(self.macs[ip],channel=self.mychan)
#            else:
#                self.e.add_peer(self.macs[ip],b'\x00' * 16,self.mychan)  
        self.verbo=False
        self.mnum=0     #message number
        self.lastipn=0 #
        self.lasttxt=''
        self.lastsnd=0 #timestamp in ms
        
    
    def macz(self,mac):
        return ubinascii.hexlify(mac,':').decode()
    
    def macbin(self,mac):
        hex_str = ''.join(f'\\x{b:02x}' for b in mac)     
        print( f"b'{hex_str}'")
        
    def laninfo(self):
        print(f"{self.wlan.status()} wlan {self.wlan.active()}, espn {self.e.active()}, conn {self.wlan.isconnected()} {self.wlan.ipconfig('addr4')[0]} ", self.macz(self.wlan.config('mac')))  

    def stats(self):
        try:
            st=self.e.stats()
            print(f"tx_pkts {st[0]}, tx_resp {st[1]}, tx_fail {st[2]}, rx_pkts {st[3]}, rx_dropped {st[4]}")
        except:
            print("8266?")

    def showmacs(self):
        for m in sorted(self.macs.items()):
            print(f"{m[0]:>3}",self.macz(m[1]))
            
    def sende(self,ipn,txt):
        self.wlan.active(True)
        self.lastipn=ipn
        self.lasttxt=txt
        self.lastsnd=time.ticks_ms()  
        self.mnum+=1
        if self.mnum > 99:
            self.mnum=1
        ms=f"M{self.mnum:02d} {txt}"
        peer=self.macs[ipn]
        res=self.e.send(peer, ms) #OSError 869 -> kein espnow active
        if self.verbo: print("Snd",ipn,ms,res)
        return res
    
    def again(self):
        self.sende(self.lastipn,self.lasttxt)
        
    def reccli(self):
        if self.verbo: print("reccli",end=" ")
        host, msg = self.e.recv(100)
        if msg:             # msg == None if timeout in recv()
            msgt=msg.decode()
            if self.verbo: print(self.ips[host], msgt)
            if msgt[0]=='M':
                return msgt[4:]
            print("reccli Invalid",msgt)
        else:
            print("reccli Nix")
            return ''
    
    def recsrv(self):
        if self.verbo: print("recsrv",end=" ")
        host, msg = self.e.recv(100)
        if msg:             # msg == None if timeout in recv()
            msgt=msg.decode()
            if self.verbo: print(self.ips[host], msgt)
            return self.ips[host], msgt
        else:
            print("Nix")
            return None
    
    def info(self):
        self.laninfo()
        self.stats()
        try:
            pes=self.e.get_peers()
            for st in pes:
                print(f'{self.ips[st[0]]:>3}',self.macz(st[0]),f"cha {st[2]}, ifi {st[3]}, encr {st[4]}")  # f"lmk {st[1]},
        except:
            print("8266!")

