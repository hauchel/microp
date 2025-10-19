# to test i2 and other funcs on ESP8266
import gc
import sys
import time
import machine 
from machine import I2C
from machine import Pin

try:
    import msvcrt
    def kbhit():
        return msvcrt.kbhit()    
    def getch():
        return msvcrt.getwch()
except ImportError:
    print("Assuming on ESP")
    import uselect
    def kbhit():
        spoll=uselect.poll()
        spoll.register(sys.stdin,uselect.POLLIN)
        kbch = sys.stdin.read(1) if spoll.poll(0) else None
        spoll.unregister(sys.stdin)
        return(kbch)
    
    def getch():
        while True:
            ch= sys.stdin.read(1)     
            if ch is not None:
                return ch


# some globals    
count=2     # number of bytes
start = time.ticks_ms()
devadr=0

pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=I2C(scl=pinSCL, sda=pinSDA)
print ("Howdy")

def info():
    gc.collect()
    print(" Free",gc.mem_free(),"Dev",devadr,"Cnt",count,)
    
def doread():
    # read one
    erg=con.readfrom(devadr,1)
    print("Read: ",erg)
        
def dowrite(data):
    print('Acks:',con.writeto(devadr,data))
          
def menu():   
    global count
    global devadr
    inpAkt=False
    inp=0
    push=0
    
    while True:
        if not inpAkt: print(devadr,">",end='')
        ch = getch()  
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
                elif ch=="a":       # accel read
                    accdau()
                elif ch=="c":       #set count
                    count=inp
                    info()                     
                elif ch=="d":       #set device
                    devadr=inp
                    info()
                elif ch=="g":       # gyro read
                    gyrdau()               
                elif ch=="h":       # pin high
                    p2 = Pin(inp, Pin.OUT)    
                    p2.on()    
                elif ch=="i":       # pin inp
                    p2 = Pin(inp, Pin.IN)
                elif ch=="l":       # pin low
                    p2 = Pin(inp, Pin.OUT)   
                    p2.off() 
                elif ch=="m":       # set mode
                   pass       
                elif ch=="n":       #reset
                    dev.reset()
                elif ch=="q":       # quit
                    print ("\brestart with ",__name__,".menu() ")
                    return
                elif ch=="r":       #read 
                    doread()
                elif ch=="s":
                    print ("speed",inp)  
                    con.init(pinSCL,pinSDA,freq=inp*1000)
                elif ch=="t":       #Temp
                    pass
                elif ch=="u":
                    print ("wake") 
                    dev.wake()                    
                elif ch=="U":
                    print ("sleep") 
                    dev.sleep()                   
                elif ch=="w":
                    dowrite(bytes([inp]))
                elif ch==",":
                    push=inp;
                    print(bytes([push]))
                elif ch=="+":
                    inp+=push
                    print ("\b",inp)
                    push=inp
                elif ch=="-":
                    inp-=push
                    print ("\b",inp)
                    push=inp                    
                elif ch=="#":
                    durch()
                else:
                    info()
                    print("?")
            except Exception as inst:
                sys.print_exception(inst)   
menu()        
