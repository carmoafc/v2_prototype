import requests
import cayenne.client
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

def on_message(message):
    import datetime
    import time

    print(datetime.datetime.now())
    print("message received: " + str(message))

    if message.channel==1:
        raspFunctions.takePhotoFCN(camera)

    if message.channel==2:
        raspFunctions.takeVideoFCN(camera)

    if message.channel==3:
        raspFunctions.updateModelFCN()

    if message.channel==4:
        xCut, yCut = raspFunctions.calibrateFCN()

    if message.channel==5: 
        # MODEL RUNNING TIME 
        # duration = 60
        #initialTime = time.time()
        while True:
            raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
            #if time.time()-initialTime >= duration:
            #    break
            time.sleep(0.1)
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + ' - Finished')

    if message.channel==6:
        global shouldStop 
        shouldStop = False

# Variables to star code and personalize all things
xCut = [0, 256]
yCut = [0, 256]
timeToStart = 30
timeToMeasure = 2

time.sleep(timeToStart)
camera = PiCamera()
point = "alpha"
shouldStop = True
client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)

filename = 'number.txt'

i = 0
while i <= 2:
    client.loop()
    if i == 0:
        raspFunctions.updateModelFCN()

        with open(filename, 'r') as file:
            number = int(file.read())

        number += 1

        with open(filename, 'w') as file:
            file.write(str(number))
            battery = 100-((number*100)/1600)

        raspFunctions.sendMensage(client, 9, battery)

    raspFunctions.obtainTemperature(client)
    raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    time.sleep(timeToMeasure)

    i = i + 1

#os.system('sudo shutdown -h now')
