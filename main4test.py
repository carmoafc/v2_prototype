import requests
import tago
import credentials
import time
import raspFunctions
from picamera import PiCamera
import serial
import os

def checkInternetRequests(url='http://www.google.com/', timeout=3):
    try:
        # Check if internet connection is available by sending a HEAD request to Google
        r = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        print(ex)
        return False

def wait_serial_string(ser, s):
    # Wait for a specific serial string to be received
    print("Waiting for serial string [%s]" % s)
    response = ""
    while s not in response:  # Wait for the message
        if ser.in_waiting > 0:  # If there is data waiting
            response = ser.readline().decode('ascii', 'ignore').rstrip()

def read_serial_string(ser):
    # Read a serial string from the serial port
    response = ""
    if ser.in_waiting > 0:  # If there is data waiting
        response = ser.readline().decode('ascii', 'ignore').rstrip()
    return response

def write_serial_string(ser, s):
    # Write a serial string to the serial port
    time.sleep(5)  # Wait for stability (you may adjust this)
    print("Writing serial string [%s]" % s)
    ser.write((s + "\n").encode('ascii', 'ignore'))

def replicate_response(ser, s):
    # Enter a loop to replicate serial data print until "END" is received
    print("Entering in loop to replicate serial data print until END")
    line = ""
    while "END" not in line:
        write_serial_string(ser, s)
        line = read_serial_string(ser)
        print(line)
        time.sleep(1)

# Variables to start the code and personalize all things
xCut = [0, 256]
yCut = [0, 256]
timeToStart = 0
timeToMeasure = 2

time.sleep(timeToStart)
point = "alpha"
shouldStop = True

while checkInternetRequests() == False:  # Wait for internet connection
    time.sleep(timeToMeasure)

# Setup serial communication
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.reset_input_buffer()

# Send "ON" command to the device
write_serial_string(ser, "ON")

# Wait for "IT" response from the device
wait_serial_string(ser, "IT")

# Read the iteration number from the device
iteration = int(read_serial_string(ser))

# Tago.io setup
client = tago.Device(credentials.tagoToken)
filename = '/home/pi/v2_prototype/number.txt'

# Read the last iteration and total from the file
last_curr = last_total = 0  # with no file, all will be ZERO
with open(filename, 'r') as f:
    line = f.readlines()[-1]  # read the last line
    last_curr, last_total = map(int, line.split("/"))

# Check if the iteration is greater than or equal to the last iteration
if iteration >= last_curr:
    if iteration > last_curr:
        # If it's the same battery, just append the iteration to the file
        with open(filename, "a") as f:
            f.write("%s/%s\n" % (iteration, last_total))
    else:
        # If it's a new battery, update the total and create a new file
        last_total = last_curr
        with open(filename, "w") as f:
            f.write("%s/%s\n" % (iteration, last_total))

    # Calculate battery percentage
    if last_total > 0:
        battery = 100 - ((iteration * 100.0) / last_total)
    else:
        battery = 100 - ((iteration * 100.0) / 10000)  # just for calibration

    # Send battery data to Tago.io
    data = {
        'variable': 'bateria',
        'value': str(battery),
        'unit': '%'
    }
    client.insert(data)

    # Perform additional functions
    raspFunctions.obtainTemperature(client)
    camera = PiCamera()
    raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    camera.close()

    # Send "SHUT" command to the device
    write_serial_string(ser, "SHUT")
    # Shutdown the Raspberry Pi
    os.system('sudo shutdown -h now')
else:
    print("ERROR")
