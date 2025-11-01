import sys, os
#import struct
from time import sleep_ms,ticks_ms
from machine import Pin, SPI
import uselect
from nrf24simple import NRF24L01


inpAkt = False
inp = 0

# Pintranslator fuer ESP8266-Boards
# LUA-Pins     D0 D1 D2 D3 D4 D5 D6 D7 D8
# ESP8266 Pins 16  5  4  0  2 14 12 13 15 
#                 SC SD
bus = 1
MISOp = Pin(12)
MOSIp = Pin(13)
SCKp  = Pin(14)
spi=SPI(1,baudrate=4000000)   #ESP8266

   

print("MISO {}, MOSI {}, SCK {}\n".format(MISOp,MOSIp,SCKp))
CSN = Pin(15, mode=Pin.OUT, value=1) 
CE =  Pin(0, mode=Pin.OUT, value=0)
nrf = NRF24L01(spi, CSN, CE, payloadSize=8)
pipeAdr=[0x5A5A5A5A54,0x5A5A5A5A52]
kanal=50
nrf.setChannel(kanal)
print("Listening/Sending on channel",kanal)
nrf.openTXPipe(pipeAdr[0])
nrf.openRXPipe(1, pipeAdr[1])
nrf.info()

poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

def hilf():
    print("""   
    s     Slave
    m     Master
    i     info
    ..k   kanal   0..125
    ..p   payload 1..32
    q     quit
    """
    )

def master():
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
    
    while durchgang < versucheMax:
        if poller.poll(0):
            try:
                return sys.stdin.read(1)
            except:
                return "?"  # unicode error
        nrf.stopListening()
        text="send:{}".format(durchgang)
        print("\nsending:", text)
        try:
            nrf.sendData(text.encode())
        except OSError:
            print("OSerr")
            pass
        nrf.startListening()
        timedOut=nrf.TimeOut(80)
        timeState=timedOut()
        while not nrf.bytesAvailable()and not timeState:
            timeState=timedOut()
        if timeState:
            print("Timeout!", durchgang)
            fehler += 1
        else:
            antwort=nrf.getData()
            print("Durchgang:",durchgang)
            response=antwort.decode()
            print("Antwort:",response.strip("\x00\n\r"))
            erfolgreich += 1
        durchgang =(durchgang+1)%256
    print("Von {} Durchgaengen waren {} erfolgreich.".\
          format(versucheMax,erfolgreich))

def slave():    
    nrf.setChannel(kanal)
    nrf.openTXPipe(pipeAdr[1])
    nrf.openRXPipe(1, pipeAdr[0])
    nrf.startListening()
    print("SLAVE-Modus: Listening on channel ",kanal)
    while True:
        if poller.poll(0):
            try:
                return sys.stdin.read(1)
            except:
                return "?"  # unicode error
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
            wert=str(1234)
            antwort=wert.encode()
            print("got:",msg)
            nrf.stopListening()
            #sleep_ms(10)
            try:
                nrf.sendData(antwort)
            except OSError:
                pass
            print("gesendet: {}".format(antwort))
            nrf.startListening()


def menu(ch):
    global inpAkt
    global inp
    global kanal
    try:
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
            if ch == "b": 
                pass
            elif ch == "a":  # accel read
                a = inp
            elif ch == "i":           
                nrf.info()
            elif ch == "k":           
                kanal=inp
                nrf.setChannel(kanal)          
                print("Kanal",kanal)
            elif ch == "m":           
                master()                
            elif ch == "p":    
                nrf.PayloadSize(inp)           
                print ("Payload",nrf.PayloadSize())
            elif ch == "q" or ch == "\x04":  # quit
                return True                
            elif ch == "s":           
                slave()
            else:
                hilf()

    except Exception as inst:
        sys.print_exception(inst)
    return False


def loop():
    while True:
        try:
            ch=sys.stdin.read(1)
        except:
            ch= "?"  # unicode error
        if menu(ch):
            break
    print("restart with ", __name__ + ".loop() ")


print(__name__, ":")
loop()
