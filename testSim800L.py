import serial

ser = serial.Serial('/dev/ttyUSB0')

ser = serial.Serial('dev/ttyUSB0',
                    baudrate=9600,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE)

data = pmd.read()
print(byte)