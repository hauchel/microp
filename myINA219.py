# rudimentär INA219
"""
from machine import I2C,Pin
pinSDA = Pin(4)  # green
pinSCL = Pin(5)  # yell
i2c = I2C(scl=pinSCL, sda=pinSDA)
from myINA219 import INA219
ina=INA219(i2c)
ina.
"""


MAX_CURRENT = 3.2 # Amps
CURRENT_LSB = MAX_CURRENT/(2**15)
R_SHUNT = 0.1 # Ohms
CALIBRATION = int(0.04096 / (CURRENT_LSB * R_SHUNT))

CONF_R = 0x00
SHUNT_V_R = 0x01
BUS_V_R = 0x02
POWER_R = 0x03
CURRENT_R = 0x04
CALIBRATION_R = 0x05

ADDRESS = 0x40

class INA219:
    def __init__(self, i2c):
        self.brng=0
        self.pg=3     # gain shunt voltage, range 0=40mV, 80, 160, 320
        self.badc = 3 #
        self.sadc = 3 #
        self.mode = 7 #
        self.i2c=i2c
        self.i2c.writeto_mem(ADDRESS, CALIBRATION_R ,(CALIBRATION).to_bytes(2, 'big'))

    def read_current(self):
        raw_current = int.from_bytes(self.i2c.readfrom_mem(ADDRESS, SHUNT_V_R, 2), 'big')
        if raw_current >> 15:
            raw_current -= 2**16
        return raw_current * CURRENT_LSB

    def read_voltage(self):
        return (int.from_bytes(self.i2c.readfrom_mem(ADDRESS, BUS_V_R, 2), 'big') >> 3) * 0.004
        
    def read_conf(self):
        x=int.from_bytes(self.i2c.readfrom_mem(ADDRESS, CONF_R, 2), 'big')
        self.mode=x&7
        x=x>>3
        self.sadc=x&15
        x=x>>4
        self.badc=x&15
        x=x>>4
        self.pg=x&3
        x=x>>2
        self.brng=x
        print("Get mode",self.mode,"sadc",self.sadc,"badc",self.badc,"pg",self.pg,"brng",self.brng)
        
    def set_conf(self):
        x=self.brng
        x=x<<2
        x = x |self.pg
        x=x<<4
        x = x | self.badc
        x=x<<4
        x = x | self.sadc
        x=x<<3
        x = x |self.mode
        print("Set mode",self.mode,"sadc",self.sadc,"badc",self.badc,"pg",self.pg,"brng",self.brng) 
        self.i2c.writeto_mem(ADDRESS,CONF_R,x.to_bytes(2, 'big'))        
        
 