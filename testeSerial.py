import serial

ser = serial.Serial('/dev/ttyUSB0',9600)
s = [0]
while True:
	read_serial=ser.readline()
	s = str(ser.readline())
	#print(s)
	print(str(s[2:4]) == 'ON')
	#print(read_serial)
	ser.write(1)