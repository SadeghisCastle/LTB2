import SerialCom
import time

port = "COM4"
baudRate = 115200
devPort = SerialCom.serialInit(port, baudRate)


command = "G92 X0 Y0 Z0"

SerialCom.commandSend(devPort, command, baudRate)


for n in range(11 ):
    print(n)
    print()
    command = f'G1 X{n} F100'
    SerialCom.commandSend(devPort, command, baudRate)
    time.sleep(1)

for n in range(10):
    a = 9-n
    print(a)
    print()
    command = f'G1 X{9-n} F100'
    SerialCom.commandSend(devPort, command, baudRate)
    time.sleep(1)

SerialCom.serialClose(devPort)