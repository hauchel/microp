# espnow Client            
# Vorsicht!               D1:
# RST                     RST
# ADC                     ADC
# EN                      GPIO16 !!!
# GPIO16  Wake zu RST     GPIO14 !!!
# GPIO14  Netwrk Start
# GPIO12
# GPIO13
# VCC                     3.3V
# Ablauf s.u.

import sys
import uselect
import machine
import time
from espn import espn

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

inpAkt=False
strmode=False
inpStr=''
inp=0
stack=[]
cmd=''           # command received
nachricht='m'    # to send
waketime=2000    # in ms 0=unendlich
dstime= 5000     # 


myn=espn()
myn.servip=55


pidef= {2:1,4:0,5:0}    #default for outports
pins = {}
for p in pidef:
    pins[p]=machine.Pin(p, machine.Pin.OUT)
    pins[p].value(pidef[p])

def setpin(pi,va):
    print ("setpin",pi,va)
    if va==0:
        pins[pi].off()
    else:
        pins[pi].on()

def pinh(pi,du):
    print ("hpin",pi,du)
    if pidef[pi]==0:
        pins[pi].on()
    else:
        pins[pi].off()
    time.sleep_ms(du)
    pins[pi].value(pidef[pi])

def deepsl(ms):
    print("Deepsl",ms)
    if myn.is32:
        from machine import deepsleep
        deepsleep(ms)
    # 8266, connect GPIO16 to the reset pin
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire 
    rtc.alarm(rtc.ALARM0, ms)
    # put the device to sleep
    machine.deepsleep()    
    print("Hä?")
 
def lightsl(ms):
    # 8266: 0 NONE, 1 LIGHT 2 MODEM
    myn.wlan.active(False)
    print("Light",myn.wlan.active()) 
    machine.lightsleep(ms)
    myn.wlan.active(True)
    
def hilf():
    print("""
    ..a     ack 0/1
    ..c     connect   0/1
    ..e     enow.active 0/1
    ..w     wlan.active 0/1
    #,..h   set # to 1 for .. ms
    i       Info  
    j       Info (esp32 only)
    m       Macs
    ..n     lightsl ..ms
    ..N     deepsl ..ms
    #,..p   set # to 0/1
    r       recv
    ..s     send to ..
    ..t     waketime
    '       string mode, send to inp after CR
    #       terminate string mode
    """)

def prompt():
    global strmode
    strmode=False
    if myn.myip !=0:
        print (myn.myip,end=">")
    else:
        print ('??',end=">")
    
def cmdin():
    global cmd
    txt=input('cmd: ')
    cmd+=txt
    print(cmd)
    
def menu(ch):   
    global strmode
    global inpStr        
    global inpAkt
    global inp
    global stack
    global nachricht
    global waketime
    try:
        print(ch,end='')
        if strmode:
            if ch=='#':
                print()
                prompt()
            elif ch=='\b':
                inpStr=inpStr[:-1]
            elif ch=="'":
                inpStr=myn.lasttxt
                print("\n'"+inpStr,end='')
            elif ch=='\n':
                print(f">{inpStr}<")
                if inpStr =='':
                    prompt()
                else:
                    myn.sende(inp, inpStr)
                    inpStr=''
                    print("'",end='')
            else:
                inpStr+=ch
            return
            
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt):
                inp = inp * 10 + (ord(ch) - 48)
            else:
                inpAkt = True
                inp = ord(ch) - 48
            return
        else:
            inpAkt=False
            if ch=="a":         #
                myn.ack = (inp!=0)
                print("ack",myn.ack)
            elif ch=="c":   
                if (inp!=0):
                    myn.conn(True)
                else:  
                    myn.wlan.disconnect()
                    print("connect is ",myn.wlan.isconnected())
            elif ch=="e":
                myn.e.active(inp!=0)
                print("ective",myn.e.active()) 
            elif ch=="h":
                pinh(stack[-1],inp)                
            elif ch=="i":
                myn.laninfo()       
                print(myn.lastipn,myn.lasttxt)               
            elif ch=="j":
                myn.info()                    
            elif ch=="m":
                print()
                myn.showmacs() 
            elif ch=="n":                
                lightsl(inp)    
            elif ch=="N":                
                deepsl(inp)                   
            elif ch=="q" or ch == '\x04':       # quit
                myn.conn(False)
                print ("restart with ",__name__+".loop() ")
                return True
            elif ch=="p":
                setpin(stack[-1],inp)
            elif ch=="r":
                myn.recv()    
            elif ch=="s":
                myn.sende(inp, nachricht)    
            elif ch=="t":
                waketime=inp
                print("wake ms", waketime)   
            elif ch=="v":       
                myn.verbo = not myn.verbo
                print("verbo", myn.verbo)   
            elif ch=="w":
                myn.wlan.active(inp!=0)
                print("wlan",myn.wlan.active())                 
            elif ch=="'":
                inpStr=''
                strmode=True
                return
            elif ch==",":
                stack.append(inp)
                return
            elif ch=="+":
                inp=inp+stack.pop()
                print('=',inp)
                return
            elif ch=="-":
                inp=stack.pop()-inp
                print('=',inp)
                return
            else:
                print("ord=",ord(ch))
                hilf()
    except Exception as inst:
        # print ("Menu",end=' ')        
        sys.print_exception(inst) 
    prompt()
    return False

def loop():
    global cmd
    lasttick=time.ticks_ms()
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
            if waketime > 0:
                difftick = time.ticks_diff(time.ticks_ms(), lasttick)
                if difftick > waketime:
                    print("Time Over!",waketime)
                    deepsl(dstime)
        except Exception as inst:
            #print ("Loop",end=' ')
            sys.print_exception(inst)   
            
# Ablauf:
# Wakeup  Netz inaktiv 
# Sammle
print("Sammle..")
time.sleep(3)
# espnow an
myn.wlan.active(True)
print("wlan",myn.wlan.active())  
myn.e.active(True)
print("ective",myn.e.active())  
# Schicke Daten an Server
if myn.sende(myn.servip, "Alle meine Entchen"):
# falls da warte etwas
    print("Succ")
else:
    print("Fail")       
prompt()                
loop()