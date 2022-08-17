import serial
import config

ser = serial.Serial(config.dev, 115200)
print("----- Start -----")

ser.write(str.encode("SKTERM\r\n"))

while True:
    read = ser.readline().decode().strip().split()
    print(read)
    if "EVENT" in read:
        if "21" in read:
            continue
        elif "27" in read:
            print("Disconnected")
            break
print("------ End ------")
