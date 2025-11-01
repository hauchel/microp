# nrf24simple.py
# Rev. 1.0 released under MIT-License
# 2022-01-14
# J. Grzesina
from time import sleep_us, ticks_ms, sleep_ms, ticks_diff
# Werte vom Datenblatt: 
# nRF24L01+ Registeradressen (Auswahl vom Datenblatt)
CONFIG    = const(0x00)
EN_AA     = const(0x01) # Enable Auto-ACK
EN_RXADDR = const(0x02) # Bit 0..5 fuer Pipe 0..5 enable 
SETUP_AW  = const(0x03)
SETUP_RETR= const(0x04)
RF_CH     = const(0x05)
RF_SETUP  = const(0x06)
STATUS    = const(0x07)
RPD       = const(0x09)
RX_ADDR_P0= const(0x0A)
TX_ADDR   = const(0x10)
RX_PW_P0  = const(0x11)
FIFO_STATE= const(0x17)
DYNPD     = const(0x1C)

# Bitwerte in CONFIG-Register 0x00 (IRQs werden nicht benutzt)
EN_CRC = const(0x08)  # enable CRC
CRCO   = const(0x04)  # CRC Laenge; 0=1 Byte, 1=2 Bytes
PWR_UP = const(0x02)  # 1=power up, 0=power down
PRIM_RX =const(0x01)  # RX/TX control; 0=PTX, 1=PRX

# Flags im RF_SETUP Register 0x06
POW_18db = const(0x00)  # -18 dBm
POW_12db = const(0x02)  # -12 dBm
POW_06db = const(0x04)  # -6 dBm
POW_00db = const(0x06)  # 0 dBm
HSPEED1  = const(0x00)  # 1MHz
HSPEED2  = const(0x08)  # 2MHz
LSPEED   = const(0x20)  # 256kHz

# STATUS Register-Flags
RX_DR  = const(0x40)  # RX Daten bereit
TX_DS  = const(0x20)  # TX Daten gesendet
MAX_RT = const(0x10)  # retransmits ueberschritten
RX_P_NO= const(0x01)  # Data-Pipe-Nummer f. eingehende Nachr.

# FIFO_STATUS Register-Flags
RX_EMPTY = const(0x01)  # RX Puffer leer
RX_FULL  = const(0x02)  # RX Puffer voll
TX_EMPTY = const(0x10)  # dto TX
TX_FULL  = const(0x20)
TX_REUSE = const(0x40)

# SETUP_AW Register Adressbreite
# 0b00 nicht erlaubt
AWIDTH3  = 0b01
AWIDTH4  = 0b10
AWIDTH5  = 0b11

# Befehlscodes
READ_REG_CMD = const(0x00)  # | Register-Nummer
WRIT_REG_CMD = const(0x20)  # | Register-Nummer
R_RX_PL_WID  = const(0x60)  # read RX payload width
R_RX_PAYLOAD = const(0x61)  # read RX payload
W_TX_PAYLOAD = const(0xA0)  # write TX payload
REUSE_TX_PL  = const(0xE3)  # reuse last payload
FLUSH_TX     = const(0xE1)  # flush TX FIFO
FLUSH_RX     = const(0xE2)  # flush RX FIFO
NOP          = const(0xFF)  # use to read STATUS register

class NRF24L01:
    # csn,ce sind Pinobjekte, Channel <= 125, 1<= payload <=32
    # spi-objekt wird vor dem Aufruf instanziert und konfiguriert
    def __init__(self, spi, csn, ce, channel=50, payloadSize=8):
        self.spi = spi
        self.csn = csn
        self.ce = ce
        self.ce.value(0)
        self.csn.value(1)
        self.payloadSize = min(32,payloadSize)
        self.buf = bytearray(1)
        self.pipe0ReadAdr = None
        self.adrBreite=5
        self.writeReg(SETUP_AW, AWIDTH5)
        if self.readReg(SETUP_AW) != AWIDTH5:
            raise OSError("nRF24L01+ Hardware not found")
        self.writeReg(DYNPD, 0b000000)
        self.setTXConfig(POW_00db, LSPEED)
#        self.setTXConfig(POW_18db, HSPEED1)
        rtime=2000
        rcnt =8
        self.writeReg(SETUP_RETR, ((rtime%250-1) << 4) | rcnt)
        self.setCRC(2)
        self.writeReg(STATUS, RX_DR | TX_DS | MAX_RT)
        self.setChannel(channel)
        self.flushRX()
        self.flushTX()
        print("nRF24L01-Constructor\nKanal:{}, Payload:{} Bytes".\
              format(channel, self.payloadSize))
        print("nRF24: CSN {}, CE {}\n".format(csn,ce))

    def writeReg(self,reg,val):
        self.csn(0) # Befehl einleiten
        self.spi.readinto(self.buf,reg | WRIT_REG_CMD)
        state=self.buf[0]
        self.spi.readinto(self.buf, val)
        self.csn(1) # SPI-Transfer beendet
        return state
        
    def writeBuffer2Reg(self,reg,buffer):
        # schreibt den Inhalt von buffer an Register reg
        self.csn(0)
        self.spi.readinto(self.buf, WRIT_REG_CMD | reg)
        self.spi.write(buffer)
        self.csn(1)
        return self.buf[0]

    def readReg(self,reg):
        self.csn(0)
        self.spi.readinto(self.buf,reg | READ_REG_CMD)
        self.spi.readinto(self.buf)
        self.csn(1)
        return self.buf[0]
    
    def readRegs(self,addr,num):
        self.csn(0)
        self.spi.readinto(self.buf, addr)
        buffer = self.spi.read(num)
        self.csn(1)
        return buffer

    def setTXConfig(self,baud,power):
        # setzt Leistung und Geschwindigkeit
        val=(self.readReg(RF_SETUP)&0b11010001)|baud|power
        self.writeReg(RF_SETUP,val)
    
    def setCRC(self,nob):
        # bestimmt Anzahl CRC-Bytes
        val = self.readReg(CONFIG) & 0b11110011
        if nob==1:
            val = val | EN_CRC
        elif nob==2:
            val |= EN_CRC | CRCO
        self.writeReg(CONFIG, val)
    
    def flushRX(self):
        # Empfangs-Buffer leeren, Kommando parameterlos
        self.csn(0)
        self.spi.readinto(self.buf, FLUSH_RX)
        self.csn(1)
        
    
    def flushTX(self):
        # Sende-Buffer leeren, Kommando parameterlos
        self.csn(0)
        self.spi.readinto(self.buf, FLUSH_TX)
        self.csn(1)

    def readStatus(self):
        # Sende-Buffer leeren, Kommando parameterlos
        self.csn(0)
        status=self.spi.readinto(self.buf, NOP)
        self.csn(1)
        return status
    
    def setChannel(self,kanal):
        # Kanalnummer setzen 0..125
        self.writeReg(RF_CH, max(0,min(kanal, 125)))

    def PayloadSize(self, size=None):
        if not size is None:
            self.payloadSize = size
        else:
            return self.payloadSize

    # adr = Adresse der Breite self.adrBreite
    # adr kommt als Integer
    def openTXPipe(self, adr):
        # Das LSByte wird zuerst geschrieben
        adrBytes=adr.to_bytes(self.adrBreite,"little")
        print("tx-Pipe:",adrBytes)
        self.writeBuffer2Reg(TX_ADDR, adrBytes) # senden
        self.writeBuffer2Reg(RX_ADDR_P0, adrBytes) # Antwort
        self.writeReg(RX_PW_P0, self.payloadSize)
    
    def openRXPipe(self, pipeID, adr):
        adrBytes=adr.to_bytes(self.adrBreite,"little")
        assert 0 <= pipeID <= self.adrBreite
        if pipeID == 0:
            self.pipe0ReadAdr = adrBytes
        # fuer Pipe 0 und 1 schreiben wir 5 Bytes
        if pipeID < 2:
            self.writeBuffer2Reg(RX_ADDR_P0 + pipeID, adrBytes)
        else:
            # sonst nur das LSByte
            self.writeReg(RX_ADDR_P0 + pipeID, adrBytes[0])
        self.writeReg(RX_PW_P0 + pipeID, self.payloadSize)
        self.writeReg(EN_RXADDR, self.readReg(EN_RXADDR) |\
                      (1 << pipeID))

    def startListening(self):
        # Chip aktivieren und auf Empfang
        self.writeReg(CONFIG, self.readReg(CONFIG) | PWR_UP |\
                      PRIM_RX)
        self.writeReg(STATUS, RX_DR | TX_DS | MAX_RT)
        if self.pipe0ReadAdr is not None:
            self.writeBuffer2Reg(RX_ADDR_P0, self.pipe0ReadAdr)
        self.flushRX()
        self.flushTX()
        self.ce(1) 
        sleep_us(130)
        
    def bytesAvailable(self,pipe=None):
        # FIFO_STATE.0 = 0 => Daten verfuegbar
        if pipe is None:
            state=not self.readReg(FIFO_STATE) & RX_EMPTY
            return state
        else:
            pipeNum=(readStatus()<<RX_P_NO) & 0x07
            return pipeNum
    
    def testCarrier(self):
        return self.readReg(RPD)
    
    def setAutoAck(self,enable=True):
        if enable:
            self.writeReg(EN_AA, 0x3F)
        else:
            self.writeReg(EN_AA, 0x00)
            
    def getData(self):
        self.csn(0)
        self.spi.readinto(self.buf, R_RX_PAYLOAD)
        buffer = self.spi.read(self.payloadSize)
        self.csn(1)
        self.writeReg(STATUS, RX_DR)
        return buffer

    def stopListening(self):
        self.ce(0) # Modul deaktivieren
        self.flushTX() # Sende- und
        self.flushRX() # Empfangsbuffer leeren

    def TimeOut(self,t):
        start=ticks_ms()
        def compare():
            return int(ticks_ms()-start) >= t
        return compare

    def sendData(self, buffer, timeout=580):
        self.transmit(buffer)
        ready = self.TimeOut(timeout)
        state = 0
        while state==0 and not ready():
            state = self.getTXState()  # 1==Fehler, 2 == OK
        if state & MAX_RT:
            raise OSError("Transmit error")

    def getTXState(self):
        # wartet auf nRF24 oder zu viele Retransmits
        state=self.readReg(STATUS) & (TX_DS | MAX_RT)
        if state:
            state=state>>4
            self.writeReg(CONFIG, self.readReg(CONFIG) \
                          & ~PWR_UP)
            self.writeReg(STATUS, RX_DR | TX_DS | MAX_RT)
        return state # 0 still sending, 2 => fertig, 1=> Fehler

    def transmit(self, buffer):
        # sendung einleiten
        self.writeReg(CONFIG, (self.readReg(CONFIG) | PWR_UP) \
                      & ~PRIM_RX)
        sleep_us(150)
        L=len(buffer)
        if L < self.payloadSize:
            buffer=buffer+bytearray(self.payloadSize-L)
        self.csn(0) # SPI an
        self.spi.readinto(self.buf, W_TX_PAYLOAD)
        self.spi.write(buffer)
        self.csn(1) # SPI aus
        self.ce(1) # Funk an
        timeOnAir=int((8*(1+self.adrBreite+self.payloadSize+2)+9)\
                   /250000*1000000)
#         timeOnAir=15
        sleep_us(timeOnAir)  
        self.ce(0) # Funk aus
        
    def info(self):
        w=self.readReg(CONFIG)
        print("PRIM_RX:", w & 0x01)
        print("PWR_UP:", (w & 0x02)>>1)
        w=self.readReg(EN_RXADDR)
        print("Aktivierte Pipes: {:08b}".format(w))
        crc=(w & 0x0C)>>2
        if crc & 0x02:
            crc=(crc and 0x01) +1
            print("CRC enabled\n Scheme {} Byte(s)".format(crc))
        afl=self.readReg(SETUP_AW)+2
        print("Adressfeldbreite: {} Bytes".format(afl))
        w=self.readReg(SETUP_RETR)
        ARD=(((w>>4) & 0x0F)+1)*250
        ARC=w & 0x0F
        print("Retransmit delay: {}".format(ARD))
        print("Retransmit count: {}".format(ARC))
        w=self.readReg(RF_CH) & 0x7F
        print("Kanal: {}".format(w))
        w=self.readReg(RF_SETUP)
        print("Baudrate: ",end="")
        if w & 0b00100000:
            print("250kbps")
        elif w & 0b00001000:
            print("2Mbps")
        else:
            print("1Mbps")
        RF_PWR=(w >> 1) & 0x03
        pwr=[-18,-12,-6,0]
        print("TX Leistung: {}dBm".format(pwr[RF_PWR]))
        rxAdrP0=self.readRegs(RX_ADDR_P0,afl)
        txAdr=self.readRegs(TX_ADDR,afl)
        print("Receive Address, pipe 0:",rxAdrP0)
        print("Transmit Address:",txAdr)
        rxAdrP1=self.readRegs(RX_ADDR_P0+1,afl)
        print("Receive Address, pipe 1:",rxAdrP1)
        for i in range(2,6):
            r=self.readReg(RX_ADDR_P0+i)
            print("Receive Address, pipe {}: {}".\
                  format(i,r.to_bytes(1,"little")))


