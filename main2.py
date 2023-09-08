import requests
import tago
import cryptocode
import credentials
import time
import raspFunctions
from picamera import PiCamera
from gpiozero import DigitalInputDevice
import os

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
timeToStart = 30
timeToMeasure = 2

time.sleep(timeToStart)
camera = PiCamera()
point = "alpha"
shouldStop = True
client = tago.Device(credentials.tagoToken)
filename = 'number.txt'

i = 0
while i <= 2:
    if i == 0:
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
    raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    time.sleep(timeToMeasure)

    i = i + 1

#os.system('sudo shutdown -h now')
