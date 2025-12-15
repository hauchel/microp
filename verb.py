# Verbindungstester ESP8266
import gc
import sys
import time
import uselect
import machine
import ssd1306

print ("Howdy",__name__)

# some globals    
pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=machine.I2C(scl=pinSCL, sda=pinSDA)
devadr=32
verbo=False

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

outs={0:1, 1:2, 2:4, 3:8, 4:16, 5:32, 6:64, 7:128, 8:0}
for k in outs: outs[k]^=255
ins={}
colo={0:'brn ', 1:'red ', 2:'orn ', 3:'yel ', 4:'vio ', 5:'gry ', 6:'whi ', 7:'bla ',8:'-- ',}

class displ():
    def __init__(self,con):
        self.disp = ssd1306.SSD1306_I2C(128, 64, con)
        self.disp.rotate(True)
        self.disp.text('disp!', 0, 0, 1)
        self.disp.show()
        self.oldtx = [''] * 6
   
    def fill(self,col):
        self.disp.fill(col)
        self.disp.show()
    
    def zeigs(self,tx): # tx list 0..5
        di=False
        for i in range(6):
            if tx[i] != self.oldtx[i]:
                di=True
                self.oldtx[i]=tx[i]
        if di:
            self.fill(0)
            for i in range(6):
                self.disp.text(tx[i], 0, i*10, 1)
            self.disp.show()


md=displ(con)


def info():
    gc.collect()
    print(" Free",gc.mem_free(),"Dev",devadr)
    
def readdev():
    # read one
    erg=con.readfrom(devadr,1)
    if verbo: print("Read: ",erg)
    return int.from_bytes(erg)
        
def writedev(data):
    ack=con.writeto(devadr,bytes([data]))
    if verbo: print('Acks:',ack)

def bitw(b):
    bits = "{:08b}".format(b)
    return bits[:4]+' '+bits[4:]

def zero_bits(byte):
    return [i for i in range(8) if not (byte >> i) & 1]    
    
def hilfe():
    print("""
    b     I2C Scan
    ..d   set device ..
    e     eval
    ..f   set I2C Frequency
    ..h ..l ..i  .. High/Low/Input
    ..j   pin value
    r     read device
    ..w   write device 
    R     hard reset
    q     quit    
    """)

def eval():
    conlis=[]
    for i in range(8):
        # generate all different conns
        nd=outs[i] & ins[i]
        if nd not in conlis:
            conlis.append(nd)
    #print(conlis)
    txl=[''] * 8
    #print("txl",txl)
    if len(conlis)==8:
        txl[1] = 'No Conns'
    else:
        zl=0
        for co in conlis:
            tx=''
            zb=zero_bits(co)   # 0 sind verbunden
            for x in zb:
                tx+=colo[x]
            #   print(zl,tx)
            txl[zl]=tx
            zl+=1
    md.zeigs(txl)
    

def durchg(dauer=False):
    global ins
    while True:
        if poller.poll(0):
            ch=sys.stdin.read(1)
            return ch
        for i in outs:   
            writedev(outs[i])
            time.sleep_ms(10)
            ins[i]=readdev()
            if verbo: print(i,bitw(ins[i]))
        writedev(outs[8])
        eval()
        
    
def menu():   
    global devadr
    global verbo
    inpAkt=False
    inp=0
    tx=['null    null','eins    <','zwo     <','drei    <','1234567890123456','1234567890123456']
    hilfe()
    
    while True:
        if not inpAkt: print(devadr,">",end='')
        ch = sys.stdin.read(1)  
        print(ch,end='')
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
        else:
            inpAkt=False
            try:
                if ch=="b":         #scan (only from 0x08 to 0x77)
                    print("\bScanning...",end=' ')
                    print(con.scan())
                elif ch=="d":   
                    devadr=inp
                    info()
                elif ch=="e":   
                    eval()                   
                elif ch=="f":
                    print ("speed",inp)  
                    con.init(pinSCL,pinSDA,freq=inp*1000)
                elif ch=="g":       # gyro read
                    pass               
                elif ch=="h":       # pin high
                    p2 = Pin(inp, Pin.OUT)    
                    p2.on()    
                elif ch=="i":       # pin inp
                    p2 = Pin(inp, Pin.IN)
                elif ch=="j":       # pin inp
                    p2 = Pin(inp, Pin.IN)
                    print(p2,"is",p2.value())                    
                elif ch=="l":       # pin low
                    p2 = Pin(inp, Pin.OUT)   
                    p2.off() 
                elif ch=="m":       # set mode
                   pass       
                elif ch=="n":       #
                    act= not wlan.active()
                    if act: connect()
                    else:
                        wlan.active(act)
                        print("\bWlan ",act)
                elif ch=="o": 
                    print("=",bitw(outs[inp]))
                    writedev(outs[inp])
                elif ch=="p": 
                   durchg()
                elif ch=="q" or ch == '\x04':       
                    print ("\brestart with ",__name__+".menu() ")
                    print ("Vergiss: sys.modules.pop('"+__name__+"', None)")
                    return
                elif ch=="r":
                    print(bitw(readdev()))
                elif ch=="R":
                    print ("Killing me ...")
                    machine.reset()         
                elif ch=="v":    
                    verbo = not verbo
                    print("verbo", verbo)   
                elif ch=="w":
                    writedev(inp)
                elif ch=="z":                    
                    md.zeigs(tx)
                else:
                    info()
                    hilfe()
            except Exception as inst:
                sys.print_exception(inst)   
menu()        
