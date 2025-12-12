import machine
import sys
import gc
import time
import ssd1306
from stepper import stepper
from makro import makro


inpAkt=False
inp=0
stack=[]
a=0
     
pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=machine.I2C(scl=pinSCL, sda=pinSDA)                   

st=stepper(con,True)

disp = ssd1306.SSD1306_I2C(128, 64, con)
disp.text('Hello!', 0, 0, 1)
disp.show()
   
mak=makro()  
mak.makread() 
   
def nullpos():
    calc.zero()
    anf = calc.docalc()
    for i in range(len(anf)):
        st.istpos[i] = anf[i]
        st.sollpos[i] = anf[i]
        
def info(a):
    if st.verbo:
        print(f": {a}A,",end='   ')
        for i in range(2):
            print (f"{st.sollpos[i]:>4}",end=' ')
        print(f" Ti {st.ticktime}")

def hilf():
    print("""
    
    ..a   select A49 (0 to 3) 
    b     I2C Scan
    ..g   goto waypoint
    d     disable all
    e     enable 
    <spc> disable
    s     stop (soll=ist)
    ..t   ticktime in us, 0=noticks
    ..f   set I2C Frequency
    ..i   set postion ist und soll
    l     loop this makro
    ..m   aktivate makro ..
    M     read makros
    !     wait exec
    #     stop all makros
    ..p   set position soll
    v     toggle verbose
    j     toggle irre
    q     quit
    r     read waypoint file
    ..w   warte .. sekunden
    ..x ..y 
    ..<  ..> change pos by ..
    ..+  ..-
    R ..W   direct read write to pcf
    """)

def tasti(b):
   mak.maksel(b)

def menu(ch,inmak):   
    global a        
    global inpAkt
    global inp
    global stack
    
    try:
        pcf=st.devpcf[a]
        if ord(ch)>128:
            tasti(ord(ch)-128)
            return False
        if ((ch >= '0') and (ch <= '9')):
            print(ch,end='')
            if (inpAkt) :
                inp = inp * 10 + (ord(ch) - 48);
            else:
                inpAkt = True;
                inp = ord(ch) - 48;
            return
        else:
            print(ch,end='')
            inpAkt=False
            if ch=="b":         #scan (only from 0x08 to 0x77)
                print("Scanning...",end=' ')
                sc=con.scan()              
                print(sc)
            elif ch=="a":       # accel read
                a=inp
            elif ch=="d":      
                st.disableall()
            elif ch=="e":
                st.enable(a)                  
            elif ch=="f":
                print ("speed",inp)  
                con.init(pinSCL,pinSDA,freq=inp*1000)
            elif ch=="g":       
                gowayp(inp)              
            elif ch=="i":      
                st.istpos[a]=inp
                st.sollpos[a]=inp
            elif ch=="j":
                st.irre = not st.irre
                print("irre",st.irre)
            elif ch=="l":      
                mak.makloop()
            elif ch=="m":
                mak.maksel(inp)  
            elif ch=="M":
                mak.makread()  
            elif ch == "n":
                mak.makinfo()            
            elif ch == "O":
                dd=inp
                print('O',dd)                
            elif ch=="p":  
               st.setpos(a,inp)
            elif ch=="q" or ch == '\x04':       # quit
                print ("restart with ",__name__+".loop() ")
                return True
            elif ch=="r":
                wayp.readwayp()
            elif ch=="R":       #read 
                st.pcfread(pcf)
            elif ch=="s":
                st.sollpos[a]=st.istpos[a]
                st.disable(a)
            elif ch=="t":       #ick
                st.ticktime=inp
            elif ch=="v":       #ick
                st.verbo = not st.verbo
                print("verbo",st.verbo)
            elif ch=="w":
                st.pause(inp)
            elif ch=="x" or ch=="X":
                calc.x=inp
                p0,p1=calc.docalc()
                if ch=="x":
                    st.setpos(0,p0)
                    st.setpos(1,p1)
            elif ch=="y" or ch=="Y":
                calc.y=inp
                p0,p1=calc.docalc()
                if ch=="y":
                    st.setpos(0,p0)
                    st.setpos(1,p1)
            elif ch==" ":
                if not inmak: 
                    st.disableall()  #space in Makro
                    mak.makstop()
            elif ch=="!":
                return  # completed
            elif ch=="#":                
                st.disableall() 
                mak.makstop()
            elif ch==",":
                stack.append(inp)
                return
            elif ch=="+":
                inp=inp+stack.pop()
                print(inp)
                return
            elif ch=="-":
                inp=stack.pop()-inp
                print(inp)
                return
            elif ch==">":
                st.setpos(a,st.sollpos[a]+inp)
            elif ch=="<":
                 st.setpos(a,st.sollpos[a]-inp)
            else:
                hilf()
        st.dirtywrite()
        if inmak: return
        info(a)
    except Exception as inst:
        sys.print_exception(inst)   
    return False

def loop():
    while True:
        ch=mak.makget()
        if ch is not None:
            #print('exe',ch)
            menu(ch,True)
            if st.polle() is not None:
                print("Key during Makro")
                mak.makstop()
            if ch != '!': continue  # ! in makro: action
        ch=st.action()
        if menu(ch,False): break
    print ("Ende")

print(__name__,':')    
loop()