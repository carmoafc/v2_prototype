import requests
import cayenne.client
import cryptocode
import credentials
import time
import raspFunctions
from picamera import PiCamera

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

    xCut = [0, 0]
    yCut = [0, 0]

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
        duration = 60
        #initialTime = time.time()
        while True:
            raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
            #if time.time()-initialTime >= duration:
            #    break
            time.sleep(0.1)
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + ' - Finished')

    if message.channel==6:
        global should_stop 
        should_stop = False

# Variables to star code and personalize all things
xCut = [0, 0]
yCut = [0, 0]
timeToStart = 60*1
timeToMeasure = 60*5

time.sleep(timeToStart)
camera = PiCamera()
point = "alpha"
should_stop = True
client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)
# client.virtualWrite(6, 0, 'digital_sensor', 'd')

# and not should_stop

i = 0
while True:
    client.loop()
    if i == 0:
        # TODO: ALL CODES UPDATE (GITHUB WGET)
        raspFunctions.updateModelFCN()
        xCut, yCut = raspFunctions.calibrateFCN()

    raspFunctions.obtainTemperature(client)
    # TODO: MEASURE OTHER THING WITHING BEING THE TEMPERATURE
    raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    time.sleep(timeToMeasure)

    if not (should_stop and checkInternetRequests):
        raspFunctions.reboot()
        break

    # TODO: IMPLEMENT SOME THING TO ECONOMY ENERGY IN THIS TIME 
    # AND WAIT THE NEW OPERATION TO PREDICT

    i = i + 1

    print(should_stop)