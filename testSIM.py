import serial
import os, time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
port = serial.Serial('/dev/tty1', baudrate=115000, timeout=1)

port.write(b'AT\r')
rcv = port.read(10)
print(rcv)
time.sleep(1)

port.write(b'ATD+5518996847195;\r')
print('Calling…')
time.sleep(5)
port.write(b'ATH\r')
print('Hang Call…')