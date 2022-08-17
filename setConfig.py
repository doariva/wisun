import serial
import config

ser = serial.Serial(config.dev, 115200)

print("----- Start -----")
# set Channel
ser.write(str.encode("SKSREG S2 " + config.channel + "\r\n"))

# set PAN ID
ser.write(str.encode("SKSREG S3 " + config.panId + "\r\n"))

# set Route-B ID
ser.write(str.encode("SKSETRBID " + config.bid + "\r\n"))

# set Password
ser.write(str.encode("SKSETPWD C " + config.bpass + "\r\n"))

print("------ End ------")
