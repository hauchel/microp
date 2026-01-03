# von https://github.com/JeanMariePrevost/mcp4725-micropython/blob/main/mcp4725.py
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

    def set_voltage(self, voltage: float) -> None:
        """
        Set DAC output voltage.
        NOTE: Cannot truly measure voltage, only used as a shorthand based on the reference voltage.
        :param voltage: Desired output voltage (0 to VCC)
        """
        value = self._voltage_to_value(voltage)
        self.set_value(value)

    def get_voltage(self) -> float:
        """
        Get current DAC output voltage.
        NOTE: Cannot truly measure voltage, only used as a shorthand based on the reference voltage.
        :return: Current voltage as float
        """
        value = self.get_value()
        return self._value_to_voltage(value)

    def set_value_norm(self, value: float) -> None:
        """
        Set DAC output using normalized value (0.0 to 1.0).
        Fast mode, does not write EEPROM.
        :param value: Float between 0.0 and 1.0 (0% to 100%)
        """
        value = max(0.0, min(1.0, float(value)))
        dac_value = int(value * 4095)
        self.set_value(dac_value)

    def get_value_norm(self) -> float:
        """Get current DAC value as normalized value (0.0 to 1.0)"""
        value = self.get_value()
        return value / 4095