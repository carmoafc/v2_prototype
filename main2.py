import requests
import cayenne.client
import cryptocode
import credentials
import time
import raspFunctions
from picamera import PiCamera
import RPi.GPIO as gpio
import os

# /usr/local/bin/python3.7 /home/pi/v2_prototype/main.py

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
# timeToStart = 60*1
# timeToMeasure = 60*5
timeToStart = 30
timeToMeasure = 2

time.sleep(timeToStart)
camera = PiCamera()
point = "alpha"
shouldStop = True
client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)

# gpio.setmode(gpio.BCM)
# gpio.setup(21, gpio.OUT)

i = 0
while i <= 2:
    client.loop()
    if i == 0:
        # TODO: ALL CODES UPDATE (GITHUB WGET)
        raspFunctions.updateModelFCN()
    #xCut, yCut = raspFunctions.calibrateFCN()

    raspFunctions.obtainTemperature(client)
    # TODO: MEASURE OTHER THING WITHING BEING THE TEMPERATURE
    raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    time.sleep(timeToMeasure)

    # if not (shouldStop and checkInternetRequests):
    #     raspFunctions.reboot()
    #     break

    # TODO: IMPLEMENT SOME THING TO ECONOMY ENERGY IN THIS TIME 
    # AND WAIT THE NEW OPERATION TO PREDICT

    i = i + 1

# gpio.output(21, 1)
#print('Desligando')
#os.system('sudo shutdown -h now')
