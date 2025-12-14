# to test i2 and other funcs on ESP8266
import gc
import sys
import network
import machine 
import ssd1306
import framebuf


# some globals    

pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=machine.I2C(scl=pinSCL, sda=pinSDA)
x = 0
y = 0
hoch=32
breit=32


class displ():
    def __init__(self,con):
        print("Howdy", __name__)
        self.disp = ssd1306.SSD1306_I2C(128, 64, con)
        self.disp.rotate(False)
        self.disp.text('disp!', 0, 0, 1)
        self.disp.show()
   
    def smile(self,x,y):
    # Load smiley face image and disp
    # The below bytearray is a buffer representation of a 32x32 smiley face image.
        smiley = bytearray(b'\x00?\xfc\x00\x00\xff\xff\x00\x03\xff\xff\xc0\x07\xe0\x07\xe0\x0f\x80\x01\xf0\x1f\x00\x00\xf8>\x00\x00|<\x00\x00<x\x00\x00\x1epx\x1e\x0e\xf0x\x1e\x0f\xe0x\x1e\x07\xe0x\x1e\x07\xe0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x07\xe1\xc0\x03\x87\xe1\xc0\x03\x87\xe1\xc0\x03\x87\xe1\xe0\x07\x87\xe0\xf0\x0f\x07\xf0\xf8\x1f\x0fp\x7f\xfe\x0ex?\xfc\x1e<\x0f\xf0<>\x00\x00|\x1f\x00\x00\xf8\x0f\x80\x01\xf0\x07\xe0\x07\xe0\x03\xff\xff\xc0\x00\xff\xff\x00\x00?\xfc\x00')
        fb = framebuf.FrameBuffer(smiley, breit, hoch, framebuf.MONO_HLSB) # load the 32x32 image binary data in to a FrameBuffer
        self.disp.blit(fb, x, y) #
        self.disp.show()   
        
    def fill(self,col):
        self.disp.fill(col)
        self.disp.show()

    
    def zeigs(self):
        m=123
        self.disp.text(f'Eins!{m:>5}', 0, 0, 1)
        self.disp.text('Twoooo!', 0, 10, 1)
        self.disp.text('Three!', 0, 20, 1)
        self.disp.text('Eins!', 0, 30, 1)
        self.disp.text('Twoooo!', 0, 40, 1)
        self.disp.text('Three!', 0, 50, 1)
        self.disp.show()

md=displ(con)

def info():
    gc.collect()
    print(" Free",gc.mem_free(),f"{x}x {y}y {breit}b {hoch}h")
  
def hilfe():
    print("""
    a     
    b     I2C Scan
    ..c   clear screen 
    ..f   set I2C Frequency
    ..h ..l ..i  .. High/Low/Input
    n     toggle network active
    o     os info
    ..r   rotate 0/1
    ..w   write device 
    R     hard reset
    s     show
    t     text at x,y
    q     quit
    ..x   
    ..y   
    
    
    """)

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
                    print("Scanning...",end=' ')
                    sc=con.scan()              
                    print(sc)                    
                elif ch=="a":       #
                    pass          
                elif ch=="c":     
                    md.disp.fill(inp)
                    md.disp.show()
                elif ch=="f":
                    print ("speed",inp)  
                    con.init(pinSCL,pinSDA,freq=inp*1000)
                elif ch=="h":     
                    hoch=inp               
                elif ch=="q" or ch == '\x04':       
                    print ("\brestart with ",__name__+".menu() ")
                    return
                elif ch=="i":
                    smile()
                elif ch=="r":
                    md.disp.rotate( inp!=0 )
                elif ch=="s":
                    md.disp.show()
                elif ch=="t":
                    md.disp.text('Text',x,y)                    
                    md.disp.show()
                elif ch=="x":       #text
                    x=inp
                elif ch=="y":       #text
                    y=inp
                elif ch=="z":       #text
                    md.disp.zeigs()                    
                else:
                    hilfe()
            except Exception as inst:
                sys.print_exception(inst)   
            info()
menu()        
