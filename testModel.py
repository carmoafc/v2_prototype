import requests
import cayenne.client
import cryptocode
import credentials
import time
import raspFunctions
from picamera import PiCamera


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

xCut = [0, 256]
yCut = [0, 256]
# timeToStart = 60*1
# timeToMeasure = 60*5
timeToStart = 1
timeToMeasure = 2

time.sleep(timeToStart)
camera = PiCamera()
point = "alpha"
shouldStop = True
client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)

xCut, yCut = raspFunctions.calibrateFCN()
raspFunctions.runModelFCN(client, camera, xCut, yCut, point)