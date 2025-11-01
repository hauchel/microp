from stepper import stepper
import machine
import sys
import gc


class calc2():
    def __init__(self):
        print ("Howdy",__name__)
        # Geometrie
        self.breit=18.0  # breite in cm
        self.hoch=22.5
        self.ppcm= 35.0  #pulse per cm Faden
        self.lnull = (self.hoch*self.hoch + self.breit*self.breit/4)**0.5
        self.zero()
    
    def zero(self):
        print("zero")
        self.x=int(self.breit/2)
        self.y=0
 
    def docalc(self):
        # linker
        dx=float(self.x)
        dy=self.hoch-self.y
        a1=(dx*dx+dy*dy)**0.5
        b1=self.lnull-a1
        t1=int(self.ppcm*b1)
        print(f"links  dx{dx:>6.2f}, dy{dy:>6.2f}, l{a1:6.2f}, {b1:8.2f}  {t1:>5}")
        #rechter
        dx=float(self.breit-self.x)
        #dy= s.o.
        a2=(dx*dx+dy*dy)**0.5
        b2=self.lnull-a2
        t2=int(self.ppcm*b2)
        print(f"rechts dx{dx:>6.2f}, dy{dy:>6.2f}, l{a2:6.2f}, {b2:8.2f}  {t2:>5}")
        return t1,t2
        

a=0     
pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=machine.I2C(scl=pinSCL, sda=pinSDA)                   
st=stepper(con,False)
calc=calc2()
inpAkt=False
inp=0


def nullpos():
    calc.zero()
    anf = calc.docalc()
    for i in range(len(anf)):
        st.istpos[i] = anf[i]
        st.sollpos[i] = anf[i]
        
def info(a):
    gc.collect()
    if st.verbo:
        pcf=st.devpcf[a]
        print("\bA",a,"Dev",st.pcfadr[pcf],"Out",st.out[pcf],"Soll",st.sollpos[a],"Ist",st.istpos[a],"Ri",st.richt[a],f"ppcm {calc.ppcm:4.1f} lnull {calc.lnull:4.1f},  Tick {st.ticktime}")
    else:
        print(f"{a}A, {calc.x:>3}x, {calc.y:>3}y,",end='   ')
        for s in st.sollpos:
            print (f"{s:>4}",end=' ')
        print()

def hilf():
    print("""
    
    ..a   select A49 (0 to 3) 
    b     I2C Scan
    ..g   goto waypoint
    ..D   set device addr ..
    e     enable 
    <spc> disable
    s     stop (soll=ist)
    ..t   ticktime in us, 0=noticks
    ..f   set I2C Frequency
    ..i   set postion ist und soll
    ..k   set ppcm/10
    ..m   set msp 0 Full, 1 Half, 2 Quarter, 3 Eight, 7 sixteen
    o     one move
    ..p   set position soll
    v     toggle verbose
    j     toggle irre
    q     quit
    r     read waypoint file
    w     show waypoints
    ..x ..y ..z
    R ..W   direct read write to pcf
    """)

def tasti(b):
    d=10
    if   b== 3:  st.setpos(0,st.istpos[0]-d)
    elif b== 4:  st.setpos(0,st.istpos[0]+d)
    elif b== 7:  st.setpos(1,st.istpos[1]-d)
    elif b== 8:  st.setpos(1,st.istpos[1]+d)
    elif b==11:  st.setpos(2,st.istpos[2]-d)
    elif b==12:  st.setpos(2,st.istpos[2]+d)
    elif b==15:  st.setpos(3,st.istpos[3]-d)
    elif b==16:  st.setpos(3,st.istpos[3]+d)
    else:
        print("tasti",b)

    
def menu(ch):   
    global a        
    global inpAkt
    global inp
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
            print(ch,end='\b\b\b\b\b')
            inpAkt=False
            if ch=="b":         #scan (only from 0x08 to 0x77)
                print("Scanning...",end=' ')
                sc=con.scan()              
                print(sc)
            elif ch=="a":       # accel read
                a=inp
            elif ch=="c":      
                pass
            elif ch=="e":
                st.enable(a)                  
            elif ch=="f":
                print ("speed",inp)  
                con.init(pinSCL,pinSDA,freq=inp*1000)
            elif ch=="g":       
                st.gowayp(inp)              
            elif ch=="i":      
                st.istpos[a]=inp
                st.sollpos[a]=inp
            elif ch=="j":
                st.irre = not st.irre
                print("irre",st.irre)
            elif ch=="k":      
                st.ppcm=float(inp)/10
            elif ch=="m":
               st.move(a)  
            elif ch == "n":
                nullpos()               
            elif ch=="p":  
               st.setpos(a,inp)
            elif ch=="q" or ch == '\x04':       # quit
                print ("restart with ",__name__+".loop() ")
                return True
            elif ch=="r":
                st.readwayp()
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
                st.showayp()
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
                st.disableall()                  
            elif ch=="+":
                st.setpos(a,st.sollpos[a]+inp)
            elif ch=="-":
                 st.setpos(a,st.sollpos[a]-inp)
            else:
                hilf()
        st.dirtywrite()
        info(a)
    except Exception as inst:
        sys.print_exception(inst)   
    return False

def loop():
    while True:
        ch=st.action()
        if menu(ch): break
    print ("Ende")

print(__name__,':')    
loop()