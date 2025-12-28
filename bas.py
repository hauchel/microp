# to test i2 and other funcs on ESP8266
import gc
import sys
import time
import network
import machine 
import os
from machine import I2C
from machine import Pin

impl=sys.implementation[2].split()[-1]  #ESP32 ESP32C3 ESP8266
print('Howdy, Running on',impl)

# some globals    
count = 2     # number of bytes
start = time.ticks_ms()
devadr = 0
if impl=='ESP32C3':
    pinSDA = machine.Pin(8)  # green
    pinSCL = machine.Pin(9)  # yell
else:
    pinSDA = machine.Pin(4)  # green
    pinSCL = machine.Pin(5)  # yell
    
con = I2C(scl=pinSCL, sda=pinSDA)
wlan = network.WLAN(network.STA_IF)
py_files = []


def info():
    gc.collect()
    print(" Free", gc.mem_free(), "Dev", devadr, "Cnt", count,)


def readdev():
    # read one
    erg = con.readfrom(devadr, 1)
    print("Read: ", erg)


def writedev(data):
    print('Acks:', con.writeto(devadr, data))


def connect():
    wlan.active(True)
    wlan.connect('FRITZ!HH', '47114711')
    #wlan.connect('NETGEAR','12345678')
    for i in range(10):
        print("Wait Connect", i)
        if wlan.isconnected():
            break
        time.sleep(1)


def osinfo():
    statvfs = os.statvfs('/')
    print('\bblock_size', statvfs[0], 'total_blocks', statvfs[2], 'free_blocks', statvfs[3])
    info()


def listfiles():
    global py_files
    py_files = [f for f in os.listdir() if f.endswith('.py')]
    py_files.sort()  # optional, makes selection deterministic
    print()
    for i in range(len(py_files)):
        print(i, py_files[i])    


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
    n     toggle network active
    o     os info
    r     read device
    ..w   write device 
    R     hard reset
    #s     soft reset
    t     tasten auf 39
    q     quit
    p     pyfiles
    ..s   show
    ..x   execute py
    ..y   import py
    
    
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
                    print(con.scan())
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
                    con.init(pinSCL, pinSDA, freq=inp * 1000)
                elif ch == "g":       # gyro read
                    pass               
                elif ch == "h":       # pin high
                    p2 = Pin(inp, Pin.OUT)    
                    p2.on()    
                elif ch == "i":       # pin inp
                    p2 = Pin(inp, Pin.IN,Pin.PULL_UP )
                elif ch == "j":       # pin inp
                    p2 = Pin(inp, Pin.IN,Pin.PULL_UP )
                    print(p2, "is", p2.value())                    
                elif ch == "l":       # pin low
                    p2 = Pin(inp, Pin.OUT)   
                    p2.off()    
                elif ch == "n":       #
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
                   listfiles()
                elif ch == "q" or ch == '\x04':       
                    print("\brestart with ", __name__ + ".menu() ")
                    print("Vergiss: sys.modules.pop('" + __name__ + "', None)")
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
                else:
                    info()
                    hilfe()
            except Exception as inst:
                sys.print_exception(inst)   
menu()        
