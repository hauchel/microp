import sys
import uselect
import machine 
import time
import gc

cmd=""
shotime=1000    # jede sekunde, set by T
shotick=0     # akt
txl = [''] * 8

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

pinSDA = machine.Pin(4)  # green
pinSCL = machine.Pin(5)  # yell  
i2c = machine.I2C(scl=pinSCL, sda=pinSDA)
print(__name__,"Scanning...", end=' ')
devs=i2c.scan()
print(devs)

if 64 in devs:
    from myINA219 import INA219
    ina=INA219(i2c)
else: ina=None

if 60 in devs:
    from mydisp import disp
    dsp = disp(i2c)
else: dsp=None

from myMenu import xmenu
men=xmenu()
men.myip=47


def show():
    txl[1]=f"{ina.read_voltage():2.3f} V"
    txl[2]=f"{ina.read_current():2.3f} A"
    print(txl[1]+" "+txl[2])
    if dsp:                #  x  y scale spac
        dsp.disp.fill(0)
        dsp.draw_text(txl[1], 0, 0)
        dsp.draw_text(txl[2], 0, 40)
        dsp.disp.show()
        
def menu(ch):   
    global shotime, shotick
    try:
        if men.mach(ch): return False
        if ch == "b": 
            print("Scanning...", end=' ')
            print(i2c.scan())
        elif ch=="c": 
            ina.read_conf()
        elif ch=="i": 
            print(f"{ina.read_current():2.3f}")
        elif ch=="q" or ch == '\x04':       # quit
            print ("restart with ",__name__+".loop() ")
            return True        
        elif ch=="r":            
            ina.brng=men.inp
            ina.set_conf()
        elif ch=="s":            
            dsp.scale=men.inp
        elif ch=="t":
            if shotick==0:
                shotick=shotime
                raws=[[], [], [], []]
                print()
                return False
            else:
                shotick=0 
        elif ch=="T":
                shotime=men.inp    
                print("Shotime",shotime)               
        elif ch=="u": 
            print(f"{ina.read_voltage():2.3f}")         
        else:
            print("ord=",ord(ch))
    except Exception as inst:
        # print ("Menu",end=' ')        
        sys.print_exception(inst) 
    men.prompt()
    return False
    
def loop():
    global cmd
    tim=time.ticks_ms()
    lastsho=tim
    men.prompt()
    while True:
        try:
            if len(cmd) !=0:
                ch=cmd[0]
                cmd=cmd[1:]
                if menu(ch): break    
            if poller.poll(0):
                ch=sys.stdin.read(1)
                if menu(ch): break
            tim=time.ticks_ms()       
            if shotick > 0:
                difftick = time.ticks_diff(tim, lastsho)
                if difftick > shotick:
                    lastsho = tim
                    show()
        except Exception as inst:
            #print ("Loop",end=' ')
            sys.print_exception(inst)

loop()
            