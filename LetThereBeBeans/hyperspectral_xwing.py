import clients.arduino_client as xwing
import numpy as np
import time

port = "COM4"
baudRate = 115200
devPort = xwing.serialInit(port, baudRate)

positions = [[0.001,0],[0.002,0],[0.003,0],[0.004,0]]

for i in positions:
    command = f"G1 X{i[0]} Y{i[1]} F50"
    xwing.commandSend(devPort, command, baudRate)
    time.sleep(2)

xwing.serialClose(devPort)