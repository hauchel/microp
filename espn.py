import sys
import time
import network
import espnow
import uselect
import ubinascii
import machine

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)


inpAkt=False
inp=0
stack=[]
cmd=''
nachricht='m'

class espn():
    # Mnn, Ann
    # broadcasts esp8266
    #   send: don't add to peer
    #   receive: von 32: geht nicht 
    def __init__(self):
        print("Howdy espn from", __name__)
        self.is32 = (sys.platform == 'esp32')
        self.macs = { 29: b'\xE8\xDB\x84\xC5\x1E\x3D', 31: b'\xc8\xc9\xa3\xc5\xfe\xfc', 
                      41: b'\xE8\xDB\x84\xDF\x94\x78', 43: b'\xE8\xDB\x84\xC5\x3C\xA7', 45: b'\xe8\xdb\x84\xdf\x4d\x30',
                      47: b'\x84\xF3\xEB\x0D\x71\x9E',
                      53: b'\xd8\xbf\xc0\r\xea\x0c'}
        if self.is32: self.macs[0]=b'\xFF\xFF\xFF\xFF\xFF\xFF' #broadcast
        self.ips={}
        for m in self.macs:
            self.ips[self.macs[m]]=m
        self.mychan=1
        self.wlan = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
        self.wlan.active(True)
        self.mymac=self.wlan.config('mac')
        self.myip=self.ips[self.mymac] # bei key error in macs aufnehmen
        print("me",self.macz(self.mymac),self.myip)        
        self.wlan.disconnect()      # MUSS bei ESP8266?
        self.e = espnow.ESPNow()
        self.e.active(True)
        for ip in self.macs:
            print(ip,self.macz(self.macs[ip]))
            if ip != self.myip:
                self.e.add_peer(self.macs[ip])
#            if self.is32:
#                self.e.add_peer(self.macs[ip],channel=self.mychan)
#            else:
#                self.e.add_peer(self.macs[ip],b'\x00' * 16,self.mychan)  
        self.ack=True
        self.verbo=True #False
        self.mnum=1
        
    
    def macz(self,mac):
        return ubinascii.hexlify(mac,':').decode()
        
    def laninfo(self):
        print(f"{self.wlan.status()} ack {self.ack}, wlan {self.wlan.active()}, espn {self.e.active()}, conn {self.wlan.isconnected()} {self.wlan.ipconfig('addr4')[0]} ", self.macz(self.wlan.config('mac')))  

    def stats(self):
        try:
            st=self.e.stats()
            print(f"tx_pkts {st[0]}, tx_resp {st[1]}, tx_fail {st[2]}, rx_pkts {st[3]}, rx_dropped {st[4]}")
        except:
            print("8266?")

    def conn(self,warte):
        print("Connecting")
        self.wlan.connect('FRITZ!HH','47114711')
        if not warte: return
        for i in range(10):
            print ("Wait Connect",i)
            if self.wlan.isconnected():
                break
            time.sleep(1)
        print("connect is ",myn.wlan.isconnected())
        
    def showmacs(self):
        for m in sorted(self.macs.items()):
            print(f"{m[0]:>3}",self.macz(m[1]))
            
    def sende(self,ipn,txt):
        self.mnum+=1
        if self.mnum > 99:
            self.mnum=1
        ms=f"M{self.mnum:02d}"
        if ipn==0:
            peer=b'\xFF\xFF\xFF\xFF\xFF\xFF'
        else:
            peer=self.macs[ipn]
        res=self.e.send(peer, ms+txt)
        print("Send",ipn,ms,res)
    
    def recv(self):
        print("Recv",end=" ")
        host, msg = self.e.recv(1000)
        if msg:             # msg == None if timeout in recv()
            msgt=msg.decode()
            print(self.ips[host], msgt)
            if msgt[0]=='A':
                return ''
            if msgt[0]=='M':
                if self.ack:
                    ant=self.e.send(host, 'A'+msgt[1:3])
                    if self.verbo: print('ack',ant)
                return msgt[3:]
            print("Invalid",msgt)
        else:
            print("Nix")
            return ''
    
    def info(self):
        self.laninfo()
        self.stats()
        try:
            pes=self.e.get_peers()
            for st in pes:
                print(f'{self.ips[st[0]]:>3}',self.macz(st[0]),f"cha {st[2]}, ifi {st[3]}, encr {st[4]}")  # f"lmk {st[1]},
        except:
            print("8266!")


myn=espn()
   
   
def deepsl(ms):
    print("Deepsl",ms)
    if myn.is32:
        from machine import deepsleep
        deepsleep(ms)

    # 8266, connect GPIO16 to the reset pin
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, ms)
    # put the device to sleep
    machine.deepsleep()    
    print("Hä?")
 
def lightsl(ms):
    #8266: 0 NONE, 1 LIGHT 2 MODEM
    pass
    
def hilf():
    print("""
    ..a   ack 0/1
    c     connect
    d     disconn
    ..e   enow.active 0/1
    ..w   wlan.active 0/1
    i     Info  
    j     Info (esp32 only)
    l     Lightsleep
    m     Macs
    ..n   deepsl
    r     Recv
    ..s   Send to ..
    '     Nachricht
    
    """)

def prompt():
    print (myn.myip,end=">")
    
def cmdin():
    global cmd
    txt=input('cmd: ')
    cmd+=txt
    print(cmd)
    
def menu(ch):   
    global a        
    global inpAkt
    global inp
    global stack
    global nachricht
    try:
        if ((ch >= '0') and (ch <= '9')):
            print(ch,end='')
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
            return
        else:
            print(ch,end='\b')
            inpAkt=False
            if ch=="a":         #
                myn.ack = (inp!=0)
                print("ack",myn.ack)
            elif ch=="c":                                
                myn.conn(True)
            elif ch=="d":  
                myn.wlan.disconnect()
                print("connect is ",myn.wlan.isconnected())
            elif ch=="e":
                myn.e.active(inp!=0)
                print("ective",myn.e.active()) 
            elif ch=="w":
                myn.wlan.active(inp!=0)
                print("wlan",myn.wlan.active()) 
            elif ch=="i":
                myn.laninfo()             
            elif ch=="j":
                myn.info()                    
            elif ch=="m":
                print()
                myn.showmacs() 
            elif ch=="n":                
                deepsl(inp)    
            elif ch=="q" or ch == '\x04':       # quit
                myn.conn(False)
                print ("restart with ",__name__+".loop() ")
                return True    
            elif ch=="r":
                myn.recv()    
            elif ch=="s":
                myn.sende(inp,nachricht)    
            elif ch=="v":       
                myn.verbo = not myn.verbo
                print("verbo",myn.verbo)   
            elif ch=="'":
                nachricht=input('Nar: ')                
            elif ch==",":
                stack.append(inp)
                return
            elif ch=="+":
                inp=inp+stack.pop()
                print(inp)
                return
            elif ch=="-":
                inp=stack.pop()-inp
                print(inp)
                return
            elif ch==">":
                st.setpos(a,st.sollpos[a]+inp)
            elif ch=="<":
                 st.setpos(a,st.sollpos[a]-inp)
            else:
                hilf()
    except Exception as inst:
        #print ("Menu",end=' ')        
        sys.print_exception(inst) 
    prompt()
    return False

def loop():
    global cmd
    while True:
        try:
            if len(cmd) !=0:
                ch=cmd[0]
                cmd=cmd[1:]
                if menu(ch): break    
            if myn.e.any():
                cmd+=myn.recv()
                if myn.verbo: print('>'+cmd+'<')
            if poller.poll(0):
                ch=sys.stdin.read(1)
                if menu(ch): break
        except Exception as inst:
            #print ("Loop",end=' ')
            sys.print_exception(inst)   
prompt()                
loop()