# classes KENNL und REGEL

class KENNL:
    def __init__(self,dac):
        self.klA=1500     # out Anfang
        self.klD=50    # Delta
        self.klE=0     # out am Ende
        self.klN=20    # Anzahl
        self.klNum=0   # akt N
        self.klOut=0   # akt O
        self.klK=10    # Ticktime
        self.tick=0    # akt
        self.klV=0
        self.klData={}
        self.dac=dac
        self.parms()
    
    def anfang(self):
        self.klOut=self.klA
        self.klData={} 
        self.setz()
        self.tick=self.klK
        self.klNum=0
        self.parms()
        
    def setz(self):
        self.dac.set_value(self.klOut)
        
    def schoen(self,val):
        if isinstance(val, int):
            return f"{val:>5}"
        elif isinstance(val, float):
            return f"{val:3.3f}"
        elif isinstance(val, list):
            tmp=""
            for w in val:
                tmp=tmp+self.schoen(w)+"  "
            return tmp
        else:
            return str(val)

    def store(self,val):
        if self.klV:
            print(f"{self.klNum:>3} {self.klOut:>5} with {self.schoen(val)}")
        self.klData[self.klOut]=val
        self.klNum+=1
        if self.klNum>self.klN:
            self.klOut=self.klE
            self.tick=0
            self.zeig()
        else:
            self.klOut+=self.klD
        self.setz()
        
    def parms(self):
        print(f"A={self.klA} D={self.klD} E={self.klE} N={self.klN} K={self.klK} V={self.klV} out={self.klOut}")
        
    def zeig(self):
        for key in sorted(self.klData):
            print(f"{key:>5} {self.schoen(self.klData[key])}")
        

class REGL:
    def __init__(self):
        # Strom in A:
        self.soll=0 
        self.abwd=[   -0.1,   -0.05, -0.01,  -0.002,  +0.002,    +0.01,   +0.05,     +0.1,      +0.2]
        self.sted=[ -50  , -10  ,  -3  ,   -1  ,    0   ,      +1,      +3,      +20      , +100,     +150 ] # wenn < abwd dieses sted
        self.stetop=len(self.sted)-1     # zeigt auf grösstes sted
        # Stellwert 0 .. 4095
        self.stell=0
        self.stellMin=1500
        self.stellMax=4095
        self.tiset=100    # Tick ms
        self.tick=0       # akt
        self.sayset=-2    # nur bei delta >1
        self.say=0        # akt
    
    def start(self,soll): # in mA
        self.soll=soll/1000.0
        self.tick=self.tiset
        self.say=1
        print(f"Soll {self.soll:2.3f} tick {self.tick} say {self.sayset}")

    def stop(self):
        self.tick=0
        print("stop")

    def regel(self,ist):
        abw=self.soll - ist
        stedelt=self.sted[self.stetop]
        for n in range(self.stetop):
            if abw < self.abwd[n]: 
                stedelt =self.sted[n]
                break
        self.stell+=stedelt
        if self.stell < self.stellMin:
            self.stell=self.stellMin
        elif self.stell > self.stellMax:
            self.stell=self.stellMax    
        if self.say >0:
            if self.say == 1:
                sags=True
                self.say=self.sayset
            else:
                sags=False   
                self.say -=1
        elif self.say <0: 
            tst=stedelt
            if tst>0: tst=-tst
            sags=self.say>=tst
        else:
            sags=False
        if sags:
            print(f"Ist {ist:2.3f}  Abw {abw:+2.3f}  Delt {stedelt:+3d} Stell {self.stell:4d}")
        return self.stell

    def info(self):
        print("Soll",self.soll,"Stell",self.stell,"Min",self.stellMin,"Max",self.stellMax,"Tick ",self.tiset,"Akt",self.tick,"Say",self.sayset)
