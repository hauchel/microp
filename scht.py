# to test stepper A4988 controlled via i2c PCF8574 on ESP8266
# Setup for 2 PCF controlling 4 A4988
#
# pcf bit                  
# 0 4 Enable    hi disabled  Pin 1
# 1 5 Step      lo>hi clocks Pin 7
# 2 6 Richt       lo / hi    Pin 8
# 3 7                        Pin 5 Reset und 6 Sleep verbinden
# Only if MSP 
# 4 msp 0                  Pin 2
# 5     1                  Pin 3
# 6     2                  Pin 4 
#   def setmsp(self):
#        self.out &= ~(7 << 4)
#        self.out |= (self.msp <<4)
        
import gc
import sys
import time
import machine 
from machine import I2C
from machine import Pin
import uselect
from helper import tast16

class stepper():
    
    def __init__(self,con):
        self.con=con
        print ("Howdy",__name__)
        self.tast=tast16(self.con)  #
        self.tastc=0            # counter for tast query
        self.tastl=0            # last pressed
        self.poller=uselect.poll()
        self.poller.register(sys.stdin,uselect.POLLIN)
  
        self.lasttick=time.ticks_us()
        self.ticktime=5000        # in us, 0 disabled
        self.acttime =   0        # in ms, diabel all after last move
        
        self.out =[255,255]       # each PCF after start
        self.dirty=[True,True]
        self.pcfadr=[32 ,33]
        #config
        self.devpcf = [0,0,1,1]   # assign pcf
        self.bitE   = [0,4,0,4]
        self.bitS   = [1,5,1,5]
        self.bitR   = [2,6,2,6]
        self.dreh   = [0,1,0,1]   # richt negiert wenn 1
        # 
        self.sollpos= [0,0,0,0]   # nur über setpos ändern sonst.. 
        self.istpos = [0,0,0,0]
        self.richt =  [1,1,1,1]    #+-1 only
        
        # waypoints
        #self.wayp=[[10,10,0,0],[100,10],[10,100,0,0],[100,100]]
        self.readwayp()

        # Geometrie
        self.breit=22.0
        self.hoch=19.0
        self.ppcm= 35.0  #pulse per cm 
        self.lnull = (self.hoch*self.hoch + self.breit*self.breit/4)**0.5
        self.x=int(self.breit/2)
        self.y=int(self.hoch/2)
 
        self.verbo= False
        self.irre=False
#        self.msp=0  #Full Step
          

    def bitw(self,b):
        bits = "{:08b}".format(b)
        return bits[:4]+' '+bits[4:]
        
    def info(self,a):
        gc.collect()
        if self.verbo:
            pcf=self.devpcf[a]
            print("\bA",a,"Dev",self.pcfadr[pcf],"Out",self.bitw(self.out[pcf]),"Soll",self.sollpos[a],"Ist",self.istpos[a],"Ri",self.richt[a],"Tick",self.ticktime)
        else:
            print("\bA",a,f"x{self.x:>4} y {self.y:>4}",end='   ')
            for s in self.sollpos:
                print (f"{s:>4}",end=' ')
            print(f"ppcm {self.ppcm:4.1f} Tick {self.ticktime}")
    
    def pcfread(self,pcf):
        # read one
        erg=self.con.readfrom(self.pcfadr[pcf],1)
        print("Read",pcf,':',self.bitw(erg[0]))
        
        
    def dowrite(self,pcf,data):
        if self.verbo:
            print("dowrite",pcf,self.bitw(data))
        acks=self.con.writeto(self.pcfadr[pcf],bytes([data]))
        #if self.verbo: print(pcf,data,'Acks:',acks)
    
    def enable(self,a): # set low
        pcf=self.devpcf[a]
        self.out[pcf] &= ~(1 << self.bitE[a])
        self.dirty[pcf]=True
        
    def disable(self,a): # set hi
        pcf=self.devpcf[a]
        self.out[pcf] |= (1 << self.bitE[a])
        self.dirty[pcf]=True
    
    def disableall(self):
        for a in range(len(self.devpcf)):
            self.disable(a)
        for p in range (len(self.pcfadr)):
            self.dowrite(p,self.out[p])
            self.dirty[p]=False                     
            
    def setricht(self,a,neuri):
        self.richt[a]=neuri   # logical counter
        pcf=self.devpcf[a]
        if self.dreh[a]==1:   # mapping to dir
            neuri=-neuri
        if neuri==1:
            self.out[pcf] |= (1 << self.bitR[a])
        else:
            self.out[pcf] &= ~(1 << self.bitR[a])
        self.enable(a)
        #self.dirty[pcf]=True set in enable
            
    def setpos(self,a,neu):
        #self.info()
        if neu == self.sollpos[a]: return;
        if self.irre: print("setze",neu)
        if neu > self.istpos[a]:
            self.setricht(a,1)
        else:
            self.setricht(a,-1)
        if self.irre: self.info(a)
        self.sollpos[a]=neu
        if self.irre: 
            print("soll gesetzt")
            self.info(a)
    
    def showayp(self):
        i=0
        for wp in self.wayp:
            print(f"{i:>3}",end='  ')
            for s in wp:
                print (f"{s:>4}",end=' ')
            i+=1
            print()
            
    def readwayp(self):
        self.wayp=[]
        file = open('wayp.txt','r')
        for line in file:
            comp=line.split()  #
            nums = [int(x) for x in comp]
            self.wayp.append(nums)
        file.close()
        self.showayp()
        
    def gowayp(self,w):
        print('waypoint',w)
        try:
            wps=self.wayp[w]
            for a in range (len(wps)):
                self.setpos(a,wps[a])
        except Exception as inst:
            sys.print_exception(inst)
        
    def move(self,a):
        pcf=self.devpcf[a]
        raus=self.out[pcf] & ~(1 << self.bitS[a]) #lo
        self.dowrite(pcf,raus)
        self.istpos[a] += self.richt[a]
        raus |= (1 << self.bitS[a])
        self.dowrite(pcf,raus)
    
    def moveall(self):
        #es wird ggf 2 mal bei gleichem pcf geschrieben, stört nicht weiter
        moved=False
        for a in range(len(self.devpcf)):
            if self.istpos[a] != self.sollpos[a]:
                moved=True
                if self.verbo:
                    print('moveall',a,self.istpos[a],self.sollpos[a])
                self.move(a)
        return moved
    
    def calc(self):
        # linker
        dx=float(self.x)
        dy=self.hoch-self.y
        a1=(dx*dx+dy*dy)**0.5
        b1=self.lnull-a1
        t1=int(self.ppcm*b1)
        print(f"links  dx{dx:>5.2f}, dy{dy:>5.2f}, {a1:8.2f} {b1:8.2f}  {t1:>5}")
        #rechter
        dx=float(self.breit-self.x)
        #dy= s.o.
        a2=(dx*dx+dy*dy)**0.5
        b2=self.lnull-a2
        t2=int(self.ppcm*b2)
        print(f"rechts dx{dx:>5.2f}, dy{dy:>5.2f}, {a2:8.2f} {b2:8.2f}  {t2:>5}")
        return t1,t2
        
        
        
    def switcha49(self,neu):
        self.a49 = neu & 3
        return self.a49
        
 
        
    def dotast(self):
        t=self.tast.taste()
        if t==self.tastl: return
        self.tastl=t
        if t!=0:
            self.gowayp(t)

    def action(self):
        while True:
            if self.poller.poll(0): return  
            if self.ticktime > 0:
                difftick=time.ticks_diff(time.ticks_us(),self.lasttick)
                if difftick >self.ticktime:
                    self.lasttick=time.ticks_us()
                    if self.moveall():
                        self.acttime=time.ticks_ms()
                    else:
                        if self.acttime !=0:
                            diff=time.ticks_diff(time.ticks_ms(),self.acttime)
                            if diff >100:
                                #print('Autozu')
                                self.acttime =0
                                self.disableall()
                    self.tastc -=1
                    if self.tastc < 1:
                        self.tastc=10 
                        self.dotast()
                        
a49=0     
pinSDA=machine.Pin(4) #green
pinSCL=machine.Pin(5) #yell
con=I2C(scl=self.pinSCL, sda=self.pinSDA)                   
st=stepper(con)
inpAkt=False
inp=0

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
    ..x ..y
    R ..W   direct read write to pcf
    """)

def menu():   
    # Aufruf nach kbhit
    try:
        ch=sys.stdin.read(1)  
    except:
        return False #unicode error
    a=a49
    pcf=devpcf[a]
    try:
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
            elif ch=="p":  
               st.setpos(a,inp)
            elif ch=="q" or ch == '\x04':       # quit
                print ("restart with ",__name__+".menu() ")
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
                st.x=inp
                p0,p1=st.calc()
                if ch=="x":
                    st.setpos(0,p0)
                    st.setpos(1,p1)
            elif ch=="y" or ch=="Y":
                st.y=inp
                p0,p1=st.calc()
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
        for p in range (len(st.pcfadr)):
            if st.dirty[p]:
                st.dowrite(p,st.out[p])
                st.dirty[p]=False                    
        st.info(a)
    except Exception as inst:
        sys.print_exception(inst)   
    st.action()

menu()