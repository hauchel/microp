from stepper import stepper
import machine
import sys
import gc


class calc4:
    # 4
    def __init__(self):
        print("Howdy Calc", __name__)
        # Geometrie
        self.breit = 46.0  # x breite in cm
        self.lang = 27.0
        self.hoch = 14.5
        self.ppcm = 35.3  # pulse per cm Faden:  200p U=5,65cm
        self.zero()

    def zero(self):
        print("zero")
        self.x = self.breit / 2.0
        self.y = self.lang / 2.0
        self.z = self.hoch

    def abst(self, dx, dy, dz):
        # alles float
        dx2 = dx * dx
        dy2 = dy * dy
        dz2 = dz * dz
        return (dx2 + dy2 + dz2) ** 0.5

    def docalc(self):
        # gerechnet wird l=Länge des Fadens für 4 Stepper
        # abhängig von .x und .y .z
        # dazu offset des Plättchens 2*2 cm in xy
        # und ofz in z
        # M0 bei breit , 0
        ofs = 1.0
        ofz = 2.2
        dx = self.breit - self.x - ofs
        dy = self.y - ofs
        dz = self.z-ofz
        a0 = self.abst(dx, dy, dz)
        t0 = int(self.ppcm * a0)
        print(f"M0  dx{dx:>5}, dy{dy:>5}, dz{dz:>5}, l{a0:6.2f}, {t0:>5}")
        # M1 bei breit, hoch
        dx = self.breit - self.x - ofs
        dy = self.lang - self.y - ofs
        a1 = self.abst(dx, dy, dz)
        t1 = int(self.ppcm * a1)
        print(f"M1  dx{dx:>5}, dy{dy:>5}, dz{dz:>5}, l{a1:6.2f}, {t1:>5}")
        # M2 bei 0,0
        dx = self.x - ofs
        dy = self.y - ofs
        a2 = self.abst(dx, dy, dz)
        t2 = int(self.ppcm * a2)
        print(f"M2  dx{dx:>5}, dy{dy:>5}, dz{dz:>5}, l{a2:6.2f}, {t2:>5}")
        # M3 bei 0,hoch
        dx = self.x - ofs
        dy = self.lang - self.y - ofs
        a3 = self.abst(dx, dy, dz)
        t3 = int(self.ppcm * a3)
        print(f"M3  dx{dx:>5}, dy{dy:>5}, dz{dz:>5}, l{a3:6.2f}, {t3:>5}")
        return t0, t1, t2, t3


a = 0
pinSDA = machine.Pin(4)  # green
pinSCL = machine.Pin(5)  # yell
con = machine.I2C(scl=pinSCL, sda=pinSDA)
st = stepper(con)
st.dreh = [1, 0, 0, 1]
calc = calc4()


inpAkt = False
inp = 0
dd=10

def nullpos():
    calc.zero()
    anf = calc.docalc()
    for i in range(len(anf)):
        st.istpos[i] = anf[i]
        st.sollpos[i] = anf[i]


nullpos()

def info(a):
    gc.collect()
    if st.verbo:
        pcf = st.devpcf[a]
        print(f"\bA{a} Dev {st.pcfadr[pcf]} Out {st.out[pcf]} Soll{st.sollpos[a]} Ist {st.istpos[a]} Ri{st.richt[a]} ppcm {calc.ppcm:4.1f} Tick {st.ticktime}")
    else:
        print(f"{a}A, {calc.x:>5}x, {calc.y:>5}y, {calc.z:>5}z,", end="    ")
        for s in st.sollpos:
            print(f"{s:>4}", end=" ")
        print()


def hilf():
    print(
        """   
    ..a   select A49 (0 to 3) 
    b     I2C Scan
    ..g   goto waypoint
    ..D   set device addr ..
    e     enable 
    <spc> disable
    s     stop (soll=ist)
    ..t   ticktime in us, 0=noticks
    ..f   set I2C Frequency in kHz
    ..i   set postion ist und soll
    ..k   set ppcm/10
    ..m   set msp 0 Full, 1 Half, 2 Quarter, 3 Eight, 7 sixteen
    ..p   set position soll
    v     toggle verbose
    j     toggle irre
    q     quit
    r     read waypoint file
    w     show waypoints
    ..x ..y ..z
    R ..W   direct read write to pcf
    """
    )


def tasti(b,d = 10):
    if b == 1:     st.setpos(0, st.istpos[0] - d)
    elif b == 5:   st.setpos(0, st.istpos[0] + d)
    elif b == 2:   st.setpos(1, st.istpos[1] - d)
    elif b == 6:   st.setpos(1, st.istpos[1] + d)
    elif b == 3:   st.setpos(2, st.istpos[2] - d)
    elif b == 7:   st.setpos(2, st.istpos[2] + d)
    elif b == 4:   st.setpos(3, st.istpos[3] - d)
    elif b == 8:   st.setpos(3, st.istpos[3] + d)
    elif b == 13:
        st.setpos(3, st.istpos[3] + d)
        st.setpos(1, st.istpos[1] + d)
    elif b == 9:
        st.setpos(3, st.istpos[3] - d)
        st.setpos(1, st.istpos[1] - d)
    elif b == 14:
        st.setpos(3, st.istpos[3] + d)
        st.setpos(2, st.istpos[2] + d)
    elif b == 10:
        st.setpos(3, st.istpos[3] - d)
        st.setpos(2, st.istpos[2] - d)
    elif b == 15:
        st.setpos(0, st.istpos[0] + d)
        st.setpos(2, st.istpos[2] + d)
    elif b == 11:
        st.setpos(0, st.istpos[0] - d)
        st.setpos(2, st.istpos[2] - d)
    elif b == 16:
        st.setpos(0, st.istpos[0] + d)
        st.setpos(1, st.istpos[1] + d)
    elif b == 12:
        st.setpos(0, st.istpos[0] - d)
        st.setpos(1, st.istpos[1] - d)

    else:
        print("tasti", b)


def menu(ch):
    global a
    global inpAkt
    global inp
    global dd
    try:
        pcf = st.devpcf[a]
        if ord(ch) > 128:
            tasti(ord(ch) - 128,dd)
            return False
        if (ch >= "0") and (ch <= "9"):
            print(ch, end="")
            if inpAkt:
                inp = inp * 10 + (ord(ch) - 48)
            else:
                inpAkt = True
                inp = ord(ch) - 48
            return
        else:
            print(ch, end="\b\b\b\b\b")
            inpAkt = False
            if ch == "b":  # scan (only from 0x08 to 0x77)
                print("Scanning...", end=" ")
                sc = con.scan()
                print(sc)
            elif ch == "a":  # accel read
                a = inp
            elif ch == "d":
                dd=inp
                print('dd',dd)
            elif ch == "e":
                st.enable(a)
            elif ch == "f":
                print("speed", inp)
                con.init(pinSCL, pinSDA, freq=inp * 1000)
            elif ch == "g":
                st.gowayp(inp)
            elif ch == "i":
                st.istpos[a] = inp
                st.sollpos[a] = inp
            elif ch == "j":
                st.irre = not st.irre
                print("irre", st.irre)
            elif ch == "k":
                calc.ppcm = float(inp) / 10
            elif ch == "m":
                st.move(a)
            elif ch == "n":
                nullpos()
            elif ch == "p":
                st.setpos(a, inp)
            elif ch == "q" or ch == "\x04":  # quit
                print("restart with ", __name__ + ".loop() ")
                return True
            elif ch == "r":
                st.readwayp()
            elif ch == "R":  # read
                st.pcfread(pcf)
            elif ch == "s":
                st.sollpos[a] = st.istpos[a]
                st.disable(a)
            elif ch == "t":  # ick
                st.ticktime = inp
            elif ch == "v":  # ick
                st.verbo = not st.verbo
                print("verbo", st.verbo)
            elif ch == "w":
                st.showayp()
            elif ch == "x" or ch == "X":
                calc.x = inp
                res = calc.docalc()
                if ch == "x":
                    for i in range(len(res)):
                        st.setpos(i, res[i])
            elif ch == "y" or ch == "Y":
                calc.y = inp
                res = calc.docalc()
                if ch == "y":
                    for i in range(len(res)):
                        st.setpos(i, res[i])
            elif ch == "z":
                calc.z = inp
                res = calc.docalc()
                for i in range(len(res)):
                    st.setpos(i, res[i])
            elif ch == " ":
                st.disableall()
            elif ch == "+":
                st.setpos(a, st.sollpos[a] + inp)
            elif ch == "-":
                st.setpos(a, st.sollpos[a] - inp)
            else:
                hilf()
        st.dirtywrite()
        info(a)
    except Exception as inst:
        sys.print_exception(inst)
    return False


def loop():
    while True:
        ch = st.action()
        if menu(ch):
            break
    print("Ende")


print(__name__, ":")
loop()
