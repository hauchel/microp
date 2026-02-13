# Server for espn
#
import sys
import uselect
import machine
import time
from espn import espn

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

nachricht='m'  # to send
antwort={44: "m", 31: "m" }     # 
ticktime=0     #

myn=espn()
print("\x1b]2;"+"Srv "+str(myn.myip)+"\x07", end="") #Teraterm title change request


from myMenu import xmenu
men=xmenu()
men.myip=myn.myip

def shoants():
    print()
    for m in sorted(antwort.items()):
            print(f"{m[0]:>3} {m[1]}")
            
def hilf():
    print("""
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
    ..t     ticktime
    string mode:
        ..ä     1    define Antwort
        ö       2
        ..ü     3  send to inp after CR
    #       terminate string mode
    """)

def menu(ch):   
    global nachricht
    global ticktime
    global antwort
    try:
        if men.mach(ch):
            if men.strrdy:
                if men.strmode==3:
                    myn.sende(men.inp,men.inpstr)
                elif men.strmode==1:
                    antwort[men.inp]=men.inpstr
                    shoants()
                men.strdone()
            return False
        inp=men.inp
        if ch=="a":         #
            pass
        elif ch=="c":   
            if (inp!=0):
                myn.conn(True)
            else:  
                myn.wlan.disconnect()
                print("connect is ",myn.wlan.isconnected())
        elif ch=="e":
            myn.e.active(inp!=0)
            print("ective",myn.e.active())           
        elif ch=="i":
            myn.laninfo()       
            print(myn.lastipn,myn.lasttxt)               
        elif ch=="j":
            myn.info()                    
        elif ch=="m":
            print()
            myn.showmacs()                  
        elif ch=="q" or ch == '\x04':       # quit
            print ("restart with ",__name__+".loop() ")
            return True
        elif ch=="r":
            myn.recv()    
        elif ch=="s":
            myn.sende(inp, nachricht)    
        elif ch=="t":
            ticktime=inp
            print("tick ms", ticktime)   
        elif ch=="v":       
            myn.verbo = not myn.verbo
            print("verbo", myn.verbo)   
        elif ch=="w":
            myn.wlan.active(inp!=0)
            print("wlan",myn.wlan.active())                 
        elif ch==" ":
            ticktime=0
            print("tick 0 ms")                   
        else:
            print("ord=",ord(ch))
            hilf()
    except Exception as inst:
        # print ("Menu",end=' ')        
        sys.print_exception(inst) 
    men.prompt()
    return False

def loop():
    global cmd
    lasttick=0
    men.prompt()
    while True:
        try:
            if myn.e.any():
                host, msg = myn.recsrv()
                myn.sende(host,antwort[host])
                print("any",host,msg)
            if poller.poll(0):
                ch=sys.stdin.read(1)
                if menu(ch): break
            if ticktime > 0:
                difftick = time.ticks_diff(time.ticks_ms(), lasttick)
                if difftick > ticktime:
                    lasttick = time.ticks_ms()
                    myn.again()
        except Exception as inst:
            #print ("Loop",end=' ')
            sys.print_exception(inst) 
            
loop()