import requests
import cayenne.client
import cryptocode
import credentials
import time
import raspFunctions

def checkInternetRequests(url='http://www.google.com/', timeout=3):
    try:
        r = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        print(ex)
        return False

def on_message(message):
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
        raspFunctions.runModelFCN()

    if message.channel==6:
        raspFunctions.breakAllFCN()

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)

i = 0
while True:
    client.loop()
    if checkInternetRequests:
        time.sleep(2)
