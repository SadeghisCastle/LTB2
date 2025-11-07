import serial
import time


def serialRead(devPort, baud_rate):

    out = devPort.readline().decode('utf-8').strip()
    
    return out

def commandSend(devPort, command, baud_rate):

    devPort.write(command.encode())
    devPort.write(b'\n')
    time.sleep(0.5)
    out = devPort.readline().decode('utf-8').strip()
    
    return out

def serialInit(serPort, baud_rate):

    devPort = serial.Serial(serPort, baud_rate)
    time.sleep(2)
    
    return(devPort)

def serialClose(devPort):
    
    devPort.close()
    
    return 0