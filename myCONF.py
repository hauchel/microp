# Configuration
class CONF:
    def __init__(self):
        self.vcc = 3.309                    # Spannung des Teilers
        self.rtop=[9830, 9830, 9830, 9830]  # Widerstand gegen vcc
        self.rntc0=[7500, 7500, 7500, 7500]  # NTC bei 25 C
        self.betar=[1.0/3850.0, 1.0/3850.0, 1.0/3850.0, 1.0/3850.0]  # 1/Beta

    def show(self):
        print (f"Vcc {self.vcc:2.3f}V")
        for i in range(4):
            print(f"{i} Rtop {self.rtop[i]:5}M Rntc{self.rntc0[i]:5} Beta {int(round(1/self.betar[i]))}B")

    def hilf(self):
        print("""
 Show:
    ..a     
    z       zeig einmal:
    t       dauer mit 
    ..T     tick in ms 
    ..Z     1,2,4,8 zeigt chan 0 1 2 3, 16 ina
    ..Y             raw
    ..W             Widerstand 
    ..X             Temp benutzt
    ..V      Vcc 
    ..,..M   rtop Kanal n z.B. 10005,0M
    ..,..B   Beta Kanal n z.B. 3085,3B
    
dac:    
    ..o     out dac 0..4095
ina:
    i       Strom
    u       Spannung
adc:
    ..c     Channel 0..3 4..7
    ..g     Gain 0=2/3*,1=1*,2=2*,3=4*,4=8*, 5=16*
    ..x     Rate 0..7
    a       read
    d       read_rev (!)
    z       zeig
Kennlinie fuer o
      k      erzeuge mit 
    ..A      Anfangswert
    ..D      Delta
    ..N      Anzahl
    ..K      kltime in ms
Regler:
    ..r      auf Soll ..
    ..R      tick
    s        single 
    ..S      zeig 0: nix, >0: zeig alle ..,  <0: nur wenn diff >=..
    .. 
 Sonst: 
    ,        push
    .        pop
    +-   
    space   Nohalt
    """)

