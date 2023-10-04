import requests
import tago
import cryptocode
import credentials
import time
import raspFunctions
from picamera import PiCamera
import os
import serial

def checkInternetRequests(url='http://www.google.com/', timeout=3):
    try:
        r = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        print(ex)
        return False

# Variables to star code and personalize all things
xCut = [0, 256]
yCut = [0, 256]
timeToStart = 0
timeToMeasure = 2

time.sleep(timeToStart)
point = "alpha"
shouldStop = True

while checkInternetRequests == False:
    time.sleep(timeToMeasure)

ser = serial.Serial('/dev/ttyUSB0',9600)

client = tago.Device(credentials.tagoToken)
filename = '/home/pi/v2_prototype/number.txt'

i = 0
while i <= 0:
    s = ser.readline()
    print(str(s[2:4]))
    if(str(s[2:4]) == 'ON'):
        with open(filename, 'w') as file:
            file.write(str(0))
            battery = 100-((0*100)/1600)
            print('A')

    else:
        print('B')
        #raspFunctions.updateModelFCN()
        with open(filename, 'r') as file:
            number = int(file.read())

        number += 1

        with open(filename, 'w') as file:
            file.write(str(number))
            battery = 100-((number*100)/1600)

    data = {
        'variable': 'bateria',
        'value': str(battery),
        'unit': '%'
    }

    client.insert(data)

    raspFunctions.obtainTemperature(client)
    camera = PiCamera()
    raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    camera.close()
    #time.sleep(timeToMeasure)

    i = i + 1

#os.system('sudo shutdown -h now')
