from time import sleep
from datetime import datetime
import serial
import config

# setup
ser = serial.Serial(config.dev, 115200)
ser.timeout = 2

print("----- Start -----")
ser.write(str.encode("SKJOIN " + config.ipv6 + "\r\n"))

while True:
    read = ser.readline().decode()
    if (read != ""):
        print(datetime.now(), end=": ")
        print(read, end="")
    sleep(1)
