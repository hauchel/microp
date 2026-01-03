from machine import I2C,Pin
pinSDA = Pin(4)  # green
pinSCL = Pin(5)  # yell
i2c = I2C(scl=pinSCL, sda=pinSDA)


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

i2c.writeto_mem(ADDRESS, CALIBRATION_R ,(CALIBRATION).to_bytes(2, 'big'))


def read_current():
    raw_current = int.from_bytes(i2c.readfrom_mem(ADDRESS, SHUNT_V_R, 2), 'big')
    if raw_current >> 15:
        raw_current -= 2**16
    return raw_current * CURRENT_LSB


def read_voltage():
    return (int.from_bytes(i2c.readfrom_mem(ADDRESS, BUS_V_R, 2), 'big') >> 3) * 0.004