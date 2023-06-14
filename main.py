import requests
import cayenne.client
import cryptocode
import credentials
import time

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
        # Todo: Take a photo
        print('')
    if message.channel==2:
        # Todo: Take a video
        print('')
    if message.channel==3:
        # Todo: Update model
        print('')
    if message.channel==4:
        # Todo: Calibrate something
        print('')
    if message.channel==5:
        # Todo: Run model
        print('')

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)

i = 0
while True:
    client.loop()
    if checkInternetRequests:
        time.sleep(2)
