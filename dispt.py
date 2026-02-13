# to test i2 and other funcs on ESP8266
import gc
import sys
import network
import machine 
import ssd1306
import framebuf

pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
i2c=machine.I2C(scl=pinSCL, sda=pinSDA)

from mydisp import disp
dsp = disp(i2c)

x = 0
y = 0
hoch=32
breit=32
txl = [''] * 8

from myMenu import xmenu
men=xmenu()
men.myip=47


def info():
    gc.collect()
    print(" Free",gc.mem_free(),f"{x}x {y}y {breit}b {hoch}h")
  
def hilfe():
    print("""
    a     
    b     I2C Scan
    ..c   clear screen 
    d     draw 1234 at x,y
    ..f   set I2C Frequency*1000, z.b. 400
  
    ..r   rotate 0/1
    ..w   write device 
    R     hard reset
    s     show
    t     text at x,y
    q     quit
    ..x   
    ..y   
    z     zeigtxe
    
    """)

def menu():   
    global x,y,breit,hoch,txl
    hilfe()
    
    while True:
        try:
            ch = sys.stdin.read(1)  
            if men.mach(ch):
                if men.strrdy:
                    if men.strmode==1:
                        txl[men.inp]=men.inpstr
                        dsp.zeigtx(txl)
                    men.strdone()
                continue
            inp=men.inp
            if ch=="b":
                print("Scanning...",end=' ')
                sc=i2c.scan()              
                print(sc)                    
            elif ch=="a":       #
                pass          
            elif ch=="c":                
                dsp.disp.fill(inp)
                dsp.disp.show()
            elif ch=="d":                
                dsp.draw_text('1234', x, y)
            elif ch=="f":
                print ("speed",inp)  
                con.init(pinSCL,pinSDA,freq=inp*1000)
            elif ch=="h":     
                hoch=inp               
            elif ch=="q" or ch == '\x04':       
                print ("\brestart with ",__name__+".menu() ")
                return
            elif ch=="i":
                dsp.smile()
            elif ch=="r":
                dsp.disp.rotate( inp!=0 )
            elif ch=="s":
                dsp.disp.show()
            elif ch=="t":
                dsp.disp.text(f"{y:2}",x,y)                    
                dsp.disp.show()
            elif ch=="x":       #text
                x=inp
            elif ch=="y":       #text
                y=inp
            elif ch=="z":       #text
                dsp.zeigtx(txl)                    
            else:
                hilfe()
        except Exception as inst:
            sys.print_exception(inst)   
        print(f"{x}x {y}y ",end='>')
menu()        
