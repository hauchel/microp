# Configuration
class CONF:
    def __init__(self):
        self.vcc = 3.272                    # Spannung des Teilers in V
        self.rtop=[6760, 6705, 6708, 6754]  # Widerstand gegen vcc
#        self.rtop=[9830, 9830, 9990, 9850]  # Widerstand gegen vcc
        self.intwid1=[17562, 16570, 16280,  16596, 14462, 13442, 12007, 11443, 10304, 9515, 8426, 7292, 5803, 4870]
        self.intwid2=[17562, 16570, 16280,  15295, 14462, 13442, 12007, 11519, 10304, 9515, 8236, 7292, 5803, 4870]
        self.intwid3=[17562, 17249, 16887,  16520, 14810, 13625, 12152, 11519, 10181, 9382, 8536, 7110, 5633, 4684]        
        self.inttmp =[ 12.5,  13.9,  14.3,   15.3,  17.2,  19.0,  21.8,  22.5,  25.3, 27.0, 28.9, 33.0, 38.5, 42.8]
        #                                                 700
        self.cmd="13z0w12x"
        
    def show(self):
        print (f"Vcc {self.vcc:2.3f}V")
        for i in range(4):
            print(f"{i} Rtop{self.rtop[i]:6}M")
    
    def showint(self):
        print("         2             3")
        i=0
        print(f"{i:2} {self.inttmp[i]:4.1f}  {self.intwid2[i]:5d}              {self.intwid3[i]:5d}")
        for i in range(1,len(self.inttmp)):
            dt=self.inttmp[i]-self.inttmp[i-1]
            dw2=self.intwid2[i]-self.intwid2[i-1]
            uw2=float(dw2)/dt
            dw3=self.intwid3[i]-self.intwid3[i-1]
            uw3=float(dw3)/dt
            print(f"{i:2} {self.inttmp[i]:4.1f}  {self.intwid2[i]:5d}  {uw2:+6.1f}  {self.intwid3[i]:5d} {uw3:+6.1f}")

    def readint(self):
        self.intwid1=[]
        self.intwid2=[]
        self.intwid3=[]
        self.inttmp=[]
        with open('temps.txt', "r") as fsrc:
            for line in fsrc:
                sp=line.split()
                self.inttmp.append(float(sp[0]))
                self.intwid1.append(int(sp[1]))
                self.intwid2.append(int(sp[2]))
                self.intwid3.append(int(sp[3]))

    def writeint(self):
        with open('temps.txt', "w") as f:
            for i in range(len(self.inttmp)):
                s=f"{self.inttmp[i]:4.1f} {self.intwid1[i]:5d} {self.intwid2[i]:5d} {self.intwid3[i]:5d} \n"
                f.write(s)
            
    def fix(self,pos,tmp,wid2,wid3):
        print(f"Fix {pos:2} {tmp:4.1f}  {wid2:5d}  {wid3:5d}")
        self.inttmp[pos]=tmp
        self.intwid2[pos]=wid2
        self.intwid3[pos]=wid3
        self.showint()
        
    def temp(self,wid,chan):
        if chan==3:
            iwi=self.intwid3
        elif chan==1:
            iwi=self.intwid1            
        elif chan==2:
            iwi=self.intwid2
        else:
            print("Invalid chan",chan)
            return 888
        if wid <= iwi[-1]:
            return 990
        if wid >= iwi[0]:
            return 999
        # passendes Intervall suchen
        for i in range(len(iwi) - 1):
            x0 = iwi[i]
            x1 = iwi[i + 1]
            if x0 >= wid >= x1:   # absteigend sortiert!
                y0 = self.inttmp[i]
                y1 = self.inttmp[i + 1]
                # lineare Interpolation
                return y0 + (wid - x0) * (y1 - y0) / (x1 - x0)

        return 995  # inconsistent table


    def hilf(self):
        print("""
 Show:
    z       zeig einmal oder
    t       dauer mit 
    ..T     tick in ms 
    ..z     1,2,4,8 zeigt chan 0 1 2 3, 16 ina, 32 lum
    ..y             raw
    ..w             Widerstand 
    ..x             Temp 
    ..V      Vcc 
    d        Min/Max raw 
    ..B      Anzahl für d, 0 nix
    ..,..W   rtop Kanal n z.B. 0,10005M
    
dac:    
    ..o     out dac 0..4095
ina:
    i       Strom
    u       Spannung
adc:
    ..c     Channel 0..3 4..7
    ..g     Gain 0=6V,1=4V,2=2V,3=1V,4=0.5V, 5=0.256V
    ..p     Rate 0..7
    a       read
Kennlinie fuer o
      k      erzeuge mit 
    ..A      Anfangswert
    ..D      Delta
    ..E      Endwert
    ..N      Anzahl
    ..K      kltime in ms
Regler:
    ..r      auf Soll in mA
    ..R      tick
    s        single 
    ..S      zeig 0: nix, >0: zeig alle ..,  <0: nur wenn diff >=..
 Sonst: 
    ,        push
    .        pop
    +-   
    space   Nothalt
    """)

