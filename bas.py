# to test i2 and other funcs on ESP8266
import gc
import sys
import time
import network
import machine 
import os
from machine import I2C
from machine import Pin
from helper import tast16

# some globals    
count=2     # number of bytes
start = time.ticks_ms()
devadr=0

pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=I2C(scl=pinSCL, sda=pinSDA)
wlan = network.WLAN(network.STA_IF)
print ("Howdy")

tast=tast16(con)

def deep_sleep(msecs):
  #configure RTC.ALARM0 to be able to wake the device
  rtc = machine.RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
  # set RTC.ALARM0 to fire after Xmilliseconds, waking the device
  rtc.alarm(rtc.ALARM0, msecs)
  #put the device to sleep
  machine.deepsleep()
  
def info():
    gc.collect()
    print(" Free",gc.mem_free(),"Dev",devadr,"Cnt",count,)
    
def doread():
    # read one
    erg=con.readfrom(devadr,1)
    print("Read: ",erg)
        
def dowrite(data):
    print('Acks:',con.writeto(devadr,data))

def connect():
    wlan.active(True)
    wlan.connect('FRITZ!HH','47114711')
    #wlan.connect('NETGEAR','12345678')
    for i in range(10):
        print ("Wait Connect",i)
        if wlan.isconnected():
            break
        time.sleep(1)

def osinfo():
    statvfs = os.statvfs('/')
    print('\bblock_size',statvfs[0],'total_blocks',statvfs[2],'free_blocks',statvfs[3])
    info()

def bitw(b):
    bits = "{:08b}".format(b)
    return bits[:4]+' '+bits[4:]
"""
def finn(b):
    if   b== 7: return 4
    elif b==11: return 3
    elif b==13: return 2
    elif b==14: return 1
    else:       return 0
    
def taste():
    tadr=39
    a=con.readfrom(tadr,1)
    if a[0]==0xF0: return 0
    #print ('\nis:',bitw(a[0]))
    con.writeto(tadr,bytes([0x0f]))
    a=con.readfrom(tadr,1)
    sp=finn(a[0] & 0xF) # 7 11 13 14
    print ('\n0f spa:',bitw(a[0]),'=',sp)
    if sp==0: return 0
    con.writeto(tadr,bytes([0xf0]))
    b=con.readfrom(tadr,1)
    zl=finn(b[0]>>4)
    print ('f0 zle:',bitw(b[0]),'=',zl)
    if zl==0: return 0
    return zl*4 + sp - 4
"""
    
def hilfe():
    print("""
    b     I2C Scan
    ..d   set device ..
    ..f   set I2C Frequency
    ..h ..l ..i  .. High/Low/Input
    n     toggle network active
    o     os info
    t     tasten auf 39
    q     quit
    
    
    """)
    
def menu():   
    global count
    global devadr
    inpAkt=False
    inp=0
    push=0
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
                elif ch=="a":       # accel read
                    accdau()
                elif ch=="c":       #set count
                    count=inp
                    info()                     
                elif ch=="d":       #set device
                    devadr=inp
                    info()
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
                   osinfo()
                elif ch=="q" or ch == '\x04':       
                    print ("\brestart with ",__name__+".menu() ")
                    print ("Vergiss: sys.modules.pop('"+__name__+"', None)")
                    return
                elif ch=="r":       #read 
                    doread()
                elif ch=="s":
                    print ("Sleep",inp)  
                    deep_sleep(inp*1000)
                elif ch=="t":       #taste
                    print(tast.taste())
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
                    hilfe()
            except Exception as inst:
                sys.print_exception(inst)   
menu()        
