# A4988 controlled via i2c PCF8574 on ESP8266
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

import sys
import time
import uselect
from helper import tast16


class stepper():

    def __init__(self, con,taston=False):
        print("Howdy", __name__)
        self.con = con       
        self.tast = tast16(self.con)  #
        self.tastc = 0  # counter for tast query
        self.tastl = 0  # last pressed
        self.taston = taston
        self.poller = uselect.poll()
        self.poller.register(sys.stdin, uselect.POLLIN)

        self.lasttick = time.ticks_us()
        self.ticktime = 5000  # in us, 0 disabled
        self.acttime = 0  # in ms, diabel all after last move

        self.out = [255, 255]  # each PCF after start
        self.dirty = [True, True]
        self.pcfadr = [32, 33]
        sc=self.con.scan()  
        for p in self.pcfadr:
            print("Dev",p,end=" ")
            if p in sc:
                print("confirmed")
            else:
                print("removed")
                self.pcfadr.remove(p)

        # config
        self.devpcf = [0, 0, 1, 1]  # assign pcf
        self.bitE = [0, 4, 0, 4]
        self.bitS = [1, 5, 1, 5]
        self.bitR = [2, 6, 2, 6]
        self.dreh = [0, 1, 1, 0]  # richt negiert wenn 1
        #
        self.sollpos = [0, 0, 0, 0]  # nur über setpos ändern sonst..
        self.istpos = [0, 0, 0, 0]
        self.richt = [1, 1, 1, 1]  # +-1 only

        # waypoints
        # self.readwayp()

        self.verbo = False
        self.irre = False

    #        self.msp=0  #Full Step

    def pcfread(self, pcf):
        # read one
        erg = self.con.readfrom(self.pcfadr[pcf], 1)
        print("Read", pcf, ":", self.bitw(erg[0]))

    def pcfwrite(self, pcf, data):
        # if self.verbo: print("pcfwr",pcf,self.bitw(data))
        try:
            self.con.writeto(self.pcfadr[pcf], bytes([data]))
        except IndexError:
            print("pcf",pcf,"nicht da")

    def enable(self, a):  # set low
        pcf = self.devpcf[a]
        self.out[pcf] &= ~(1 << self.bitE[a])
        self.dirty[pcf] = True

    def disable(self, a):  # set hi
        pcf = self.devpcf[a]
        self.out[pcf] |= 1 << self.bitE[a]
        self.dirty[pcf] = True

    def dirtywrite(self):
        for p in range(len(self.pcfadr)):
            if self.dirty[p]:
                self.dirty[p] = False
                self.pcfwrite(p, self.out[p])

    def disableall(self):
        for a in range(len(self.devpcf)):
            self.disable(a)
        self.dirtywrite()

    def setricht(self, a, neuri):
        self.richt[a] = neuri  # logical counter
        pcf = self.devpcf[a]
        if self.dreh[a] == 1:  # mapping to dir
            neuri = -neuri
        if neuri == 1:
            self.out[pcf] |= 1 << self.bitR[a]
        else:
            self.out[pcf] &= ~(1 << self.bitR[a])
        self.enable(a)
        # self.dirty[pcf]=True set in enable

    def setpos(self, a, neu):
        # self.info()
        if neu == self.sollpos[a]:
            return
        if self.irre:
            print("setze", neu)
        if neu > self.istpos[a]:
            self.setricht(a, 1)
        else:
            self.setricht(a, -1)
        if self.irre:
            self.info(a)
        self.sollpos[a] = neu
        if self.irre:
            print("soll gesetzt")
            self.info(a)

    def showayp(self):
        i = 0
        for wp in self.wayp:
            print(f"{i:>3}", end="  ")
            for s in wp:
                print(f"{s:>4}", end=" ")
            i += 1
            print()

    def readwayp(self):
        self.wayp = []
        try:
            with open("wayp.txt", "r") as file:
                for line in file:
                    comp = line.split()  #
                    nums = [int(x) for x in comp]
                    self.wayp.append(nums)
        except Exception as inst:
            sys.print_exception(inst)
            self.wayp = [[10, 10, 0, 0], [100, 10], [10, 100, 0, 0], [100, 100]]
        self.showayp()

    def gowayp(self, w):
        print("waypoint", w)
        try:
            wps = self.wayp[w]
            for a in range(len(wps)):
                self.setpos(a, wps[a])
        except Exception as inst:
            sys.print_exception(inst)

    def move(self, a):
        pcf = self.devpcf[a]
        raus = self.out[pcf] & ~(1 << self.bitS[a])  # lo
        self.pcfwrite(pcf, raus)
        self.istpos[a] += self.richt[a]
        raus |= 1 << self.bitS[a] # to hi clocks
        self.pcfwrite(pcf, raus)

    def moveall(self):
        # TODO: es wird ggf 2 mal bei gleichem pcf geschrieben, stört nicht weiter
        moved = False
        for a in range(len(self.devpcf)):
            if self.istpos[a] != self.sollpos[a]:
                moved = True
                # if self.verbo: print('moveall',a,self.istpos[a],self.sollpos[a])
                self.move(a)
        return moved

    def action(self):
        # loops until key pressed or taste (+128)
        while True:
            if self.poller.poll(0):
                try:
                    return sys.stdin.read(1)
                except:
                    return "?"  # unicode error
            if self.ticktime > 0:
                difftick = time.ticks_diff(time.ticks_us(), self.lasttick)
                if difftick > self.ticktime:
                    self.lasttick = time.ticks_us()
                    if self.moveall():
                        self.acttime = time.ticks_ms()
                    else:
                        if self.acttime != 0:
                            diff = time.ticks_diff(time.ticks_ms(), self.acttime)
                            if diff > 100:
                                # print('Autozu')
                                self.acttime = 0
                                self.disableall()
                    if self.taston:
                        self.tastc -= 1
                        if self.tastc < 1:
                            self.tastc = 10
                            t = self.tast.taste()
                            if t != 0:
                                return chr(t + 128)
