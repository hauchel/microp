# von https://github.com/JeanMariePrevost/mcp4725-micropython/blob/main/mcp4725.py
"""
from 
from machine import I2C,Pin
pinSDA = Pin(4)  # green
pinSCL = Pin(5)  # yell   
i2c = I2C(scl=pinSCL, sda=pinSDA)
"""

class MCP4725:
    def __init__(self, i2c, address: int = 0x60, vcc: float = 3.3) -> None:
        """
        Initialize MCP4725 DAC.
        :param i2c: Initialized machine.I2C instance
        :param address: I2C address (default 0x60)
        :param vcc: Supply voltage (default 3.3V) (Only used as a reference for set_voltage and get_voltage)
        """
        self.i2c = i2c
        self.address = address
        self.vcc = vcc

    # ======================
    # BASIC OPERATIONS
    # ======================

    def set_value(self, value: int) -> None:
        """
        Set raw DAC output value (12 bit integer, 0-4095)
        Fast mode, does not write EEPROM.
        :param value: 12-bit integer (0-4095)
        """
        value = max(0, min(4095, int(value)))
        buf = bytearray(3)
        buf[0] = 0x40  # Fast mode command
        buf[1] = value >> 4
        buf[2] = (value & 0xF) << 4
        self.i2c.writeto(self.address, buf)

    def get_value(self) -> int:
        """Get current raw DAC value (12 bit integer, 0-4095)"""
        buf = self.i2c.readfrom(self.address, 5)
        return ((buf[1] << 4) | (buf[2] >> 4)) & 0xFFF

