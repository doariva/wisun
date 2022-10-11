import serial
import config

ser = serial.Serial(config.dev, 115200)
print("----- Start -----")
ser.write(str.encode("SKLL64 " + config.macAddr + "\r\n"))
print(ser.readline().decode(), end="")  # echoback
print(ser.readline().decode(), end="")  # data
print("------ End ------")
