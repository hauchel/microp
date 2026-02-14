# to test i2 and other funcs on ESP8266
import gc
import sys
import time
import machine 
import os
import network
from machine import I2C,Pin

impl=sys.implementation[2].split()[-1]  #ESP32 ESP32C3 ESP8266
print(__name__,"Running on",impl)

# some globals    
count = 2     # number of bytes
start = time.ticks_ms()
devadr = 0
if impl=='ESP32C3':
    pinSDA = machine.Pin(8)  # green q
    pinSCL = machine.Pin(9)  # yell
else:
    pinSDA = machine.Pin(4)  # green
    pinSCL = machine.Pin(5)  # yell
    
i2c = I2C(scl=pinSCL, sda=pinSDA)
wlan = network.WLAN(network.STA_IF)
py_files = []

def info():
    gc.collect()
    print(" Free", gc.mem_free(), "Dev", devadr, "Cnt", count,)

def readdev():
    # read one
    erg = i2c.readfrom(devadr, 1)
    print("Read: ", erg)

def writedev(data):
    print('Acks:', i2c.writeto(devadr, data))

def osinfo():
    statvfs = os.statvfs('/')
    print('\bblock_size', statvfs[0], 'total_blocks', statvfs[2], 'free_blocks', statvfs[3])
    info()

def list_py():
    global py_files
    py_files = [f for f in os.listdir() if f.endswith('.py')]
    py_files.sort()
    print()
    for i in range(len(py_files)):
        print(f"{i:2d} {py_files[i]}")    

def list_mpy():
    global py_files
    py_files = [f for f in os.listdir() if f.endswith('.mpy')]
    py_files.sort()
    print()
    for i in range(len(py_files)):
        print(f"{i:2d} {py_files[i]}")    


def deepsl(ms):
    print("Deepsl",impl,ms)
    # 8266, connect GPIO16 to the reset pin
    # configure RTC.ALARM0 to be able to wake the device
    if impl=='ESP8266':
        rtc = machine.RTC()
        rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
        # set RTC.ALARM0 to fire 
        rtc.alarm(rtc.ALARM0, ms)
        # put the device to sleep
        machine.deepsleep()    
        print("Hä?")
    else:
        from machine import deepsleep
        deepsleep(ms)
 
def lightsl(ms):
    # 8266: 0 NONE, 1 LIGHT 2 MODEM
    wlan.active(False)
    print("Light",myn.wlan.active()) 
    machine.lightsleep(ms)
    wlan.active(True)
    

def reset_info():
    r = machine.reset_cause()
    print("Cause", r, end=' ')
    if r == machine.PWRON_RESET: print('Power')
    elif r == machine.HARD_RESET: print('Hard')
    elif r == machine.WDT_RESET: print('WDT')
    elif r == machine.DEEPSLEEP_RESET: print('Deep')
    elif r == machine.SOFT_RESET: print('Soft')
    else: print('?')


def bitw(b):
    bits = "{:08b}".format(b)
    return bits[:4] + ' ' + bits[4:]


def hilfe():
    print("""
    a     reset_cause
    b     I2C Scan
    ..d   set device ..
    ..f   set I2C Frequency
    ..h ..l ..i  .. High/Low/Input
    ..j   pin value
    m     modules
    e     toggle network active
    ..n     lightsl ..ms
    ..N     deepsl ..ms
    o     os info
    r     read device
    ..w   write device 
    R     hard reset
    #s     soft reset
    t     tasten auf 39
    q     quit
    p     py files
    P     mpy 
    ..s   show
    ..x   execute py
    ..y   import py
    ..z   zap (remove) py
    """)


def menu():   
    global count
    global devadr
    inpAkt = False
    inp = 0
    hilfe()

    while True:
        if not inpAkt: print(devadr, ">", end='')
        ch = sys.stdin.read(1)  
        print(ch, end='')
        if ((ch >= '0') and (ch <= '9')):
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48)
            else:
                inpAkt = True;
                inp = ord(ch) - 48
        else:
            inpAkt = False
            try:
                if ch == "b":  # scan (only from 0x08 to 0x77)
                    print("\bScanning...", end=' ')
                    print(i2c.scan())
                elif ch == "a":       #
                    reset_info()
                elif ch == "c":  # set count
                    count = inp
                    info()                     
                elif ch == "d":  # set device
                    devadr = inp
                    info()
                elif ch == "f":
                    print("speed", inp)  
                    i2c.init(pinSCL, pinSDA, freq=inp * 1000)
                elif ch == "g":       # gyro read
                    pass               
                elif ch == "h":       # pin high
                    p2 = Pin(inp, Pin.OUT)    
                    p2.on()    
                elif ch == "i":       # pin inp
                    p2 = Pin(inp, Pin.IN,Pin.PULL_UP )
                    print(p2, "is", p2.value())  
                elif ch == "j":       # pin inp
                    info()
                                      
                elif ch == "l":       # pin low
                    p2 = Pin(inp, Pin.OUT)   
                    p2.off()    
                elif ch=="n":                
                    lightsl(inp)    
                elif ch=="N":                
                    deepsl(inp)                         
                elif ch == "e":       #
                    act = not wlan.active()
                    if act: connect()
                    else:
                        wlan.active(act)
                        print("\bWlan ", act)
                elif ch == "m": 
                   print(sys.modules())
                elif ch == "o": 
                   osinfo()
                elif ch == "p": 
                   list_py()
                elif ch == "P": 
                   list_mpy()
                elif ch == "q" or ch == '\x04':       
                    print("\brestart with ", __name__ + ".menu() ")
                    return
                elif ch == "r":  # read 
                    readdev()
                elif ch == "R":
                    print("Killing me ...")
                    machine.reset()
                elif ch == "s":
                    file = open(py_files[inp], 'r')
                    print()
                    print(file.read())
                    file.close()
                elif ch == "t":  # taste
                    pass        
                elif ch == "w":
                    writedev(bytes([inp]))
                elif ch == "x":         
                    exec(open(py_files[inp]).read())
                elif ch == "y":
                    module_name = py_files[inp][:-3]  # remove ".py"
                    print("Importing module:", module_name)
                    mod = __import__(module_name)
                    print("\n back in", __name__)
                elif ch == "z":
                    filnam=py_files[inp]
                    print ("Zapping",filnam)
                    os.remove(filnam)
                   
                else:
                    info()
                    hilfe()
            except Exception as inst:
                sys.print_exception(inst)   
menu()        
