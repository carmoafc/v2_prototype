import time
import RPi.GPIO as gpio
import os

gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.OUT)

gpio.output(21, 1)

print('Desligando')
os.system('sudo shutdown -h now')