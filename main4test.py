import requests
import tago
import credentials
import time
import raspFunctions
from picamera import PiCamera
import serial
import os
import RPi.GPIO as GPIO
import datetime

# Configurar o pino GPIO 21 para entrada
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)
GPIO.setup(20, GPIO.OUT)

def checkInternetRequests(url="http://www.google.com/", timeout=3):
    try:
        # Check if internet connection is available by sending a HEAD request to Google
        r = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        print(ex)
        return False

# Variables to start the code and personalize all things
xCut = [0, 256]
yCut = [0, 256]
timeToStart = 0
timeToMeasure = 2

time.sleep(timeToStart)
point = "beta"
shouldStop = True

time_begin = time.time()
time_const = 120
i = 0

while checkInternetRequests() == False:  # Wait for internet connection
    time.sleep(timeToMeasure)
    time_passed = time.time() - time_begin

    if time_passed >= time_const:
        i = 2
        break

# Tago.io setup
client = tago.Device(credentials.tagoToken)
raspFunctions.send_log(client, option=0)

output_msg = raspFunctions.conect_vpn()
raspFunctions.send_log(client, option=8, msg_personalize=output_msg)

filename = "/home/pi/v2_prototype/number.txt"
filename_send = "/home/pi/v2_prototype/data_send.txt"
GPIO.output(20, GPIO.LOW)

raspFunctions.send_log(client, option=1)

while i <= 0:
    if GPIO.input(21) == True:
        #raspFunctions.updateModelFCN()
        with open(filename, "r") as file:
            number = int(file.read())

        number += 1

        with open(filename, "w") as file:
            file.write(str(number))
            battery = 100-((number*100)/1600)

            #print("A")

        raspFunctions.send_log(client, option=6)
        raspFunctions.download_git()

    else:
        with open(filename, "w") as file:
            file.write(str(0))
            battery = 100-((0*100)/1600)
            #print("B")


    temperature_float = raspFunctions.obtainTemperature()
    raspFunctions.send_log(client, option=2)
    camera = PiCamera()
    index = raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    camera.close()
    raspFunctions.send_log(client, option=3)

    result = raspFunctions.compare_and_replace_date()

    current_date = datetime.datetime.now()
    str_date = current_date.strftime("%d-%m-%Y %H:%M")
    if not result:
        with open(filename_send, "a") as file:
            file.write(str_date + ", " + index + "\n")
    else:
        raspFunctions.send_report(client, filename_send)
        raspFunctions.send_log(client, option=7)

        with open(filename_send, "w") as file:
            file.write("Data completa, Classe\n" + str_date + ", " + index + "\n")

    i = i + 1

    raspFunctions.send_log_monitoring(client, index, battery, temperature_float)

GPIO.output(20, GPIO.HIGH)
raspFunctions.send_log(client, option=5)
time.sleep(1)

raspFunctions.disconect_vpn()
#os.system("sudo shutdown -h now")
GPIO.cleanup()
