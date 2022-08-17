from time import sleep
from datetime import datetime
import serial
import config

ser = serial.Serial(config.dev, 115200)
print("----- Start -----")

ser.write(str.encode("SKSCAN 2 FFFFFFFF 6\r\n"))

while True:
    read = ser.readline().decode()
    parse = read.strip().split()
    if (read != ""):
        print(datetime.now(), end=": ")
        print(read, end="")
        if "EVENT" in parse and "22" in parse:
            print("Scan Success")
            break
    sleep(1)
print("------ End ------")
