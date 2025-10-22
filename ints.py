import machine
import time, gc,sys

gc.disable()
pin12 = machine.Pin(12, machine.Pin.IN)

N = 100
times = [0]*N
levels = [0]*N
idx = 0

def irq_handler(p):
    global idx
    times[idx] = time.ticks_us()
    levels[idx] = p.value()
    idx = (idx + 1) % N

pin12.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
        handler=irq_handler)

pwm = machine.PWM(machine.Pin(14), freq=400, duty=512)        
        
def hilfe():
    print("""
    PWM auf GPIO 14
    ..d   set Duty ..
    ..f   set Frequency
    ..h ..l ..i  .. High/Low/Input
    Sample auf GPIO12
    c     clear
    s     show last samples (0..idx)
    q     quit
    
    
    """)
def info():
    print (f"freq {pwm.freq():>4} duty {pwm.duty():>4}")

def samples():
    print(idx)
    j=idx-20
    if j<1:j=1  
    for i in range (20):
        diff= time.ticks_diff(times[j],times[j-1])
        print(f"{j:>3}  {levels[j]} {diff:>5}")
        j+=1
        
def menu():   
    inpAkt=False
    inp=0
    push=0
    print(__name__,': pwm 14 irq 12')
    hilfe()
    
    while True:
        if not inpAkt: print(">",end='')
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
                elif ch=="c":       #
                    for i in range(len(times)):
                        times[i]=0
                        levels[i]=0
                    samples()
                elif ch=="d":       #
                    pwm.duty(inp)
                    info()
                elif ch=="f":       #
                    pwm.freq(inp)
                    info()                    
                elif ch=="i":       #
                    info()
                elif ch=="q" or ch == '\x04':
                    return
                elif ch=="s":       #
                    samples()                    
                else:
                    info()
            except Exception as inst:
                sys.print_exception(inst)   
menu()        

