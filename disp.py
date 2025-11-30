# to test i2 and other funcs on ESP8266
import gc
import sys
import network
import machine 
import ssd1306
import framebuf


print ("Howdy",__name__)

# some globals    

pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=machine.I2C(scl=pinSCL, sda=pinSDA)
x = 0
y = 0
hoch=32
breit=32
display = ssd1306.SSD1306_I2C(128, 64, con)
display.text('Hello!', 0, 0, 1)
display.show()

def info():
    gc.collect()
    print(" Free",gc.mem_free(),f"{x}x {y}y {breit}b {hoch}h")
  
def hilfe():
    print("""
    a     reset_cause
    b     I2C Scan
    ..d   set device ..
    ..f   set I2C Frequency
    ..h ..l ..i  .. High/Low/Input
    n     toggle network active
    o     os info
    r     read device
    ..w   write device 
    R     hard reset
    s     show
    t     tasten auf 39
    q     quit
    ..x   
    ..y   
    
    
    """)

def smile():
# Load smiley face image and display
# The below bytearray is a buffer representation of a 32x32 smiley face image.
    smiley = bytearray(b'\x00?\xfc\x00\x00\xff\xff\x00\x03\xff\xff\xc0\x07\xe0\x07\xe0\x0f\x80\x01\xf0\x1f\x00\x00\xf8>\x00\x00|<\x00\x00<x\x00\x00\x1epx\x1e\x0e\xf0x\x1e\x0f\xe0x\x1e\x07\xe0x\x1e\x07\xe0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x07\xe1\xc0\x03\x87\xe1\xc0\x03\x87\xe1\xc0\x03\x87\xe1\xe0\x07\x87\xe0\xf0\x0f\x07\xf0\xf8\x1f\x0fp\x7f\xfe\x0ex?\xfc\x1e<\x0f\xf0<>\x00\x00|\x1f\x00\x00\xf8\x0f\x80\x01\xf0\x07\xe0\x07\xe0\x03\xff\xff\xc0\x00\xff\xff\x00\x00?\xfc\x00')
    fb = framebuf.FrameBuffer(smiley, breit, hoch, framebuf.MONO_HLSB) # load the 32x32 image binary data in to a FrameBuffer
    display.blit(fb, x, y) #
    display.show()    
    
def menu():   
    global x,y,breit,hoch
    inpAkt=False
    inp=0
    push=0
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
                if ch=="b":
                    breit=inp
                elif ch=="a":       #
                    reset_info()
                elif ch=="c":       #set count
                    display.fill(0)                         # fill entire screen with colour=0
                    display.show()
                elif ch=="f":
                    print ("speed",inp)  
                    con.init(pinSCL,pinSDA,freq=inp*1000)
                elif ch=="h":     
                    hoch=inp               
                elif ch=="q" or ch == '\x04':       
                    print ("\brestart with ",__name__+".menu() ")
                    print ("Vergiss: sys.modules.pop('"+__name__+"', None)")
                    return
                elif ch=="i":
                    smile()
                elif ch=="s":
                    display.show()
                elif ch=="t":
                    display.text('Text',x,y)                    
                    display.show()
                elif ch=="x":       #text
                    x=inp
                elif ch=="y":       #text
                    y=inp
                else:
                    hilfe()
            except Exception as inst:
                sys.print_exception(inst)   
            info()
menu()        
