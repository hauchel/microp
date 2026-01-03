# ina219.py
# Hardwaretreiber fuer den INA219
class INA219:
    HWADR=const(0x40)
    
    # Register
    RegConfig=const(0x00)
    RegUShunt=const(0x01)
    RegUBus=const(0x02)
    RegPower=const(0x03)
    RegCurrent=const(0x04)
    RegCalibrate=const(0x05)
    
    # RST-Bit
    RST=const(1<<15)

    # Umax am Bus
    Ubus16V=const(0)
    Ubus32V=const(1<<13)
    ubus=["16V","32V"]

    # Abschwaecher
    PGA1=const(0) # 40mV
    PGA2=const(1) # 80mV
    PGA4=const(2) # 160mV
    PGA8=const(3) # 320mV
    PGAShift=const(11)
    PGAMask = const(3<<11)
    pga=["PGA1: 40mV","PGA2: 80mV","PGA4: 160mV","PGA8: 320mV",]
 
    # Aufloesung
    Res9=const(0)  # 9-Bit @ 84µs
    Res10=const(1) # 10-Bit @ 148µs
    Res11=const(2) # 11-Bit @ 276µs
    Res12=const(3) # 12-Bit @ 532µs
    Samp2=const(9) # 12-Bit 2x @ 1060µs
    Samp4=const(10) # 12-Bit 4x @ 2,13ms
    Samp8=const(11) # 12-Bit 8x @ 4,26ms
    Samp16=const(12) # 12-Bit 16x @ 8,51ms
    Samp32=const(13) # 12-Bit 32x @ 17,02ms
    Samp64=const(14) # 12-Bit 64x @ 34,05ms
    Samp128=const(15) # 12-Bit 128x @ 68,10ms
    BusShift=const(7)
    ShuntShift=const(3)
    BusMask=const(15<<7)
    ShuntMask=const(15<<3)
    res={
        0 :"Res9: 9-Bit @ 84µs",
        1 :"Res10: 10-Bit @ 148us",
        2 :"Res11: 11-Bit @ 276us",
        3 :"Res12: 12-Bit @ 532us",
        9 :"Samp2: 12-Bit 2x @ 1060us",
        10 :"Samp4: 12-Bit 4x @ 2,13ms",
        11 :"Samp8: 12-Bit 8x @ 4,26ms",
        12 :"Samp16: 12-Bit 16x @ 8,51ms",
        13 :"Samp32: 12-Bit 32x @ 17,02ms",
        14 :"Samp64: 12-Bit 64x @ 34,05ms",
        15 :"Samp128: 12-Bit 128x @ 68,10ms",
        }
    
    ModePowerDown=const(0)
    ModeADCoff=const(4)
    ModeUShunt=const(5)
    ModeUBus=const(6)
    ModeBoth=const(7)
    ModeMask=const(7)
    mode={
        0:"Power down",
        4:"ADC off",
        5:"Shunt-Spannung",
        6:"Bus-Spannung",
        7:"Bus- und Shunt-Spannung",
        }
    
    CnvRdy=const(1)
    Ovfl=const(0)

    def __init__(self, i2c, mode=ModeBoth, busres=Samp4,
                 shuntres=Samp4, shuntpga=PGA1, ubus= Ubus16V,
                 Imax=0.4, Rshunt=0.1):
        self.i2c=i2c
        print("Constructor of INA219")
        self.imax=Imax
        self.rshunt=Rshunt
        self.configure(mode=mode, busres=busres,
                       shuntres=shuntres, shuntpga=shuntpga,
                       ubus=ubus, Imax=Imax,Rshunt=Rshunt)
        
    
    def configure(self,mode=None, busres=None,
                 shuntres=None, shuntpga=None, ubus=None,
                 Imax=None, Rshunt=None):
        self.readConfig()
        aenderung=False
        if ubus is not None:
            self.setBusrange(ubus)
        if shuntpga is not None:
            self.setPGAShunt(shuntpga)
        if busres is not None:
            self.setBusResolution(busres)
        if shuntres is not None:
            self.setShuntResolution(shuntres)
        if mode is not None:
            self.setMode(mode)
        if Imax is not None:
            self.imax=Imax
            aenderung=True
        if Rshunt is not None:
            self.rshunt=Rshunt
            aenderung=True
        if aenderung:
            self.currentLSB=self.imax/32768
            self.cal=int(0.04096/(self.currentLSB*self.rshunt)*\
                         91.7/90.69824)
            self.writeReg(RegCalibrate,self.cal)
            print("Kalibrierfaktor: {}".format(self.cal))
        print("Konfigurationsbits:")
        self.printData(self.config)
        
    def tellMode(self,val):
        return self.mode[val]
    
    def tellResolution(self,val):
        return self.res[val]
    
    def tellPGA(self,val):
        return self.pga[val]
    
    def tellUbus(self,val):
        return self.ubus[val]
    
    def tellConfig(self):
        print("Spannungsbereich:",
              self.tellUbus(self.getBusrange()))
        print("PGA Abschwaechung:",
              self.tellPGA(self.getPGAShunt()))
        print("Bus Aufloesung:",
              self.tellResolution(self.getBusResolution()))
        print("Shunt Aufloesung:",
              self.tellResolution(self.getShuntResolution()))
        print("Modus:",self.tellMode(self.getMode()))
        
    def getCalibration(self):
        return self.cal
        
    def writeReg(self, regnum, data):
        buf=bytearray(3)
        buf[2]=data & 0xff # 
        buf[1]=data >> 8   # HIGH-Byte first (big endian)
        buf[0]=regnum
        self.i2c.writeto(HWADR,buf)

    def readReg(self, regnum):
        buf=bytearray(2)
        buf[0]=regnum
        self.i2c.writeto(HWADR,buf[0:1])
        buf=self.i2c.readfrom(HWADR,2)
        return buf[0]<<8 | buf[1]
    
    def readConfig(self):
        self.config = self.readReg(RegConfig)

    def writeConfig(self):
        self.writeReg(RegConfig,self.config)
    
    def getConfig(self):
        self.readConfig()
        return self.config
    
    def getBusrange(self):
        self.readConfig()
        return (self.config & Ubus32V) >> Ubus32V
        
    def setBusrange(self,data=Ubus16V):
        assert data in [0,1,16,32]
        c=self.config & (0xFFFF - Ubus32V)
        if data in [1,32]:
            c=c | Ubus32V
        self.config=c
        self.writeConfig()
        
    def getPGAShunt(self):
        self.readConfig()
        c=(self.config & PGAMask) >> PGAShift
        return c
    
    def setPGAShunt(self,data=PGA1):
        assert data in range(0,4)
        self.readConfig()
        c=self.config & (0xFFFF - PGAMask)
        c=c | (data << PGAShift)
        self.config=c
        self.writeConfig()
        
    def getBusResolution(self):
        self.readConfig()
        c=(self.config & BusMask) >> BusShift
        return c
    
    def setBusResolution(self,data=Samp4):
        assert data in [0,1,2,3,9,10,11,12,13,14,15]
        self.readConfig()
        c=self.config & (0xFFFF - BusMask)
        c=c | (data << BusShift)
        self.config=c
        self.writeConfig()
        
    def getShuntResolution(self):
        self.readConfig()
        c=(self.config & ShuntMask) >> ShuntShift
        return c
    
    def setShuntResolution(self,data=Samp4):
        assert data in [0,1,2,3,9,10,11,12,13,14,15]
        self.readConfig()
        c=self.config & (0xFFFF - ShuntMask)
        c=c | (data << ShuntShift)
        self.config=c
        self.writeConfig()
        
    def getMode(self):
        self.readConfig()
        c=self.config & ModeMask
        return c

    def setMode(self,data=ModeBoth):
        assert data in [0,4,5,6,7]
        self.readConfig()
        c=self.config & (0xFFFF - ModeMask)
        c=c | data
        self.config=c
        self.writeConfig()        
            
    def printReg(self, data):
        print("{:08b}".format(data[0]),\
              "{:08b}".format(data[1]))

    def printData(self, data):
        print("{:08b}".format(data >> 8),\
              "{:08b}".format(data & 0xff))

    def getShuntVoltage(self):
        raw=self.readReg(RegUShunt)
        if raw & 1<<15:
            raw = -(65536 - raw) 
        return raw / 100 # mV
    
    def getBusVoltage(self): 
        return (self.readReg(RegUBus) >>3) * 4 / 1000# V

    def getPower(self):
        if not (self.readReg(RegUBus) & (1<<Ovfl)):
            return self.readReg(RegPower)*20*self.currentLSB # W
        else:
            raise OverflowError             

    def getCurrent(self):
        if not (self.readReg(RegUBus) & (1<<Ovfl)):
            raw = self.readReg(RegCurrent)*self.currentLSB
            if raw > 32767:
                raw -= 65536
            return raw # A
        else:
            raise OverflowError

