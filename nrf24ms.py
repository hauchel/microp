# master+slave.py
# import webrepl_setup
# > d fuer disable
# Dann RST; Neustart!
import sys, os
from time import sleep_ms,ticks_ms
from machine import Pin, SPI, ADC
from nrf24simple import NRF24L01
# -------------------------------------------------------
#master=False; slave=True
master=True; slave=False
# -------------------------------------------------------

led=Pin(2,Pin.OUT,value=1)
def blink(led,pulse,wait,inverted=False,repeat=1):
    for i in range(repeat):
        if inverted:
            led.off()
            sleep_ms(pulse)
            led.on()
            sleep_ms(wait)
        else:
            led.on()
            sleep_ms(pulse)
            led.off()
            sleep_ms(wait)
            
if master and slave:
    blink(led,500,100,inverted=True,repeat=5)
    raise OSError ("ENTWEDER slave ODER master!")

chip=sys.platform
taste=Pin(0,Pin.IN,Pin.PULL_UP)
if chip == 'esp8266':
    # Pintranslator fuer ESP8266-Boards
    # LUA-Pins     D0 D1 D2 D3 D4 D5 D6 D7 D8
    # ESP8266 Pins 16  5  4  0  2 14 12 13 15 
    #                 SC SD
    bus = 1
    MISOp = Pin(12)
    MOSIp = Pin(13)
    SCKp  = Pin(14)
    spi=SPI(1,baudrate=4000000)   #ESP8266
    # # alternativ virtuell mit bitbanging
    # spi=SPI(-1,baudrate=4000000,sck=SCK,mosi=MOSI,\
    #         miso=MISO,polarity=0,phase=0)  #ESP8266
    if slave:
        adc=ADC(0)
        
elif chip == 'esp32':
    bus = 1
    MISOp= Pin(15)
    MOSIp= Pin(13)
    SCKp = Pin(14)
    spi=SPI(1,baudrate=4000000,sck=Pin(14),mosi=Pin(13),\
            miso=Pin(15),polarity=0,phase=0)  # ESP32
    if slave:
        adc=ADC(Pin(39)) # Pin SP
        adc.atten(ADC.ATTN_11DB)
        adc.width(ADC.WIDTH_12BIT)
else:
    blink(led,800,100,inverted=True,repeat=5)
    raise OSError ("Unbekannter Port")
    
print("Hardware-Bus {}: Pins fest vorgegeben".format(bus))
print("MISO {}, MOSI {}, SCK {}\n".format(MISOp,MOSIp,SCKp))

CSN = Pin(4, mode=Pin.OUT, value=1)
CE =  Pin(5, mode=Pin.OUT, value=0)
nrf = NRF24L01(spi, CSN, CE, payloadSize=8)
pipeAdr=[0x5A5A5A5A54,0x5A5A5A5A52]
kanal=50

if master:
    versucheMax = 5
    erfolgreich = 0
    fehler  = 0
    durchgang = 0
    nrf.setChannel(kanal)
    print("MASTER-Mode: Sending on channel ",kanal)
    nrf.openTXPipe(pipeAdr[0])
    nrf.openRXPipe(1, pipeAdr[1])
    nrf.startListening()
    print("MASTER-Modus, sende {} Pakete".format(versucheMax))
    nrf.info()
    
    while durchgang < versucheMax:
        nrf.stopListening()
        text="send:{}".format(durchgang)
        print("\nsending:", text)
        try:
            nrf.sendData(text.encode())
        except OSError:
            pass
        nrf.startListening()
        timedOut=nrf.TimeOut(80)
        timeState=timedOut()
        while not nrf.bytesAvailable()and not timeState:
            timeState=timedOut()
        if timeState:
            print("Timeout!", durchgang)
            fehler += 1
            blink(led,50,200,inverted=True)
        else:
            antwort=nrf.getData()
            print("Durchgang:",durchgang)
            response=antwort.decode()
            print("Antwort:",response.strip("\x00\n\r"))
            erfolgreich += 1
        blink(led,50,4950,inverted=True)
        durchgang =(durchgang+1)%256
    print("Von {} Durchgaengen waren {} erfolgreich.".\
          format(versucheMax,erfolgreich))
    
if slave:
    nrf.setChannel(kanal)
    nrf.openTXPipe(pipeAdr[1])
    nrf.openRXPipe(1, pipeAdr[0])
    nrf.info()
    nrf.startListening()
    print("SLAVE-Modus: Listening on channel ",kanal)
    while True:
        buffer = b''
        if nrf.bytesAvailable():
            #print(".",end='')
            while nrf.bytesAvailable():
                recv=nrf.getData()
                print(recv)
                buffer = buffer+recv
                sleep_ms(15)
            msg=buffer.decode()
            pos=msg.find(":")
            wert=str(adc.read())
            antwort=wert.encode()
            print("got:",msg)
            nrf.stopListening()
            #sleep_ms(10)
            try:
                nrf.sendData(antwort)
                blink(led,50,250,inverted=True)
            except OSError:
                pass
            print("gesendet: {}".format(antwort))
            nrf.startListening()
        if taste.value()==0:
            sys.exit()

