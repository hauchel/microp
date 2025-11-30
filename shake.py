from stepper import stepper
import machine
import sys
import gc
import time

a=0     
pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=machine.I2C(scl=pinSCL, sda=pinSDA)                   
st=stepper(con,False)
inpAkt=False
inp=0
stack=[]
dd=5


class makro():
    def __init__(self):
        print("Howdy", __name__)
        self.maktxt=['5555t','0p']
        self.makakt=''
    
    def makget(self):
        if self.makakt=='': return None
        else:
            c=self.makakt[0]
            self.makakt=self.makakt[1:]
            return c
    
    def maksel(self,n):
        self.makakt=self.maktxt[n]
        print ('Makro',n,self.makakt)

    def makstop(self):
        self.makakt=''
        print("makstop")
        
    def makshow(self):
        i = 0
        for m in self.maktxt:
            print(f"{i:>3}  {m}<")
            i += 1
        
    def makread(self):
        self.maktxt = ['0!'] # gleuch Zeilennummer in Datei 
        try:
            with open("makros.txt", "r") as file:
                for line in file:
                    self.maktxt.append(line.rstrip('\n \r'))
        except Exception as inst:
            sys.print_exception(inst)      
        self.makshow()
        
        
   
   
mak=makro()  
mak.makread() 
   
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
        print("\bA",a,"Dev",st.pcfadr[pcf],"Out",st.out[pcf],"Soll",st.sollpos[a],"Ist",st.istpos[a],"Ri",st.richt[a],f"Tick {st.ticktime}")
    else:
        print(f"{a}A,",end='   ')
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
    ..m   aktivate makro ..
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


def menu(ch,inmak):   
    global a        
    global inpAkt
    global inp
    global stack
    global dd
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
                gowayp(inp)              
            elif ch=="i":      
                st.istpos[a]=inp
                st.sollpos[a]=inp
            elif ch=="j":
                st.irre = not st.irre
                print("irre",st.irre)
            elif ch=="k":      
                st.ppcm=float(inp)/10
            elif ch=="m":
                mak.maksel(inp)  
            elif ch=="M":
                mak.makread()  
            elif ch == "n":
                nullpos()            
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
                time.sleep(inp)
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
                if not inmak: st.disableall()  #space in Makro
            elif ch=="!":
                print("!")
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
            if ch != '!': continue
            print("Makpaus")
        ch=st.action()
        if menu(ch,False): break
    print ("Ende")

print(__name__,':')    
loop()