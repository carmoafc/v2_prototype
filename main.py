import requests
import cayenne.client
import cryptocode
import credentials
import time
import raspFunctions
import subprocess

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
        raspFunctions.takePhotoFCN()

    if message.channel==2:
        raspFunctions.takeVideoFCN()

    if message.channel==3:
        raspFunctions.updateModelFCN()

    if message.channel==4:
        raspFunctions.calibrateFCN()

    if message.channel==5:
        duration = 60
        initialTime = time.time()
        while True:
            raspFunctions.runModelFCN(client)
            if time.time()-initialTime >= duration:
                break
            time.sleep(0.1)

    if message.channel==6:
        global should_stop
        should_stop = True

should_stop = False
client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)
client.virtualWrite(6, 0)

i = 0
while True:
    client.loop()
    if checkInternetRequests and not should_stop:
        time.sleep(2)
    else:
        raspFunctions.reboot()