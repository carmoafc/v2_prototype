import requests
import tago
import credentials
import time
import raspFunctions
from picamera import PiCamera
import serial

def checkInternetRequests(url='http://www.google.com/', timeout=3):
    try:
        r = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        print(ex)
        return False
    
def wait_serial_string(ser, s):
  print("Waiting for serial string [%s]"%(s))
  response = ""
  while(s not in response):#wait for message
    print(ser.in_waiting)
    if (ser.in_waiting > 0):#if have data waiting
      response = ser.readline().decode('ascii').rstrip()
      print(response)

def read_serial_string(ser):
    response = ""
    if (ser.in_waiting > 0):#if have data waiting
        response = ser.readline().decode('ascii').rstrip()
    
    print("Read serial string [%s]"%(response))
    return response

def write_serial_string(ser, s):
    print(f"Writing serial string [{s}]")
    print((s + '\n').encode('utf-8'))
    ser.write((s + '\n').encode('utf-8'))

# Variables to star code and personalize all things
xCut = [0, 256]
yCut = [0, 256]
timeToStart = 0
timeToMeasure = 2

time.sleep(timeToStart)
point = "alpha"
shouldStop = True

while checkInternetRequests == False: #witing internet connection
    time.sleep(timeToMeasure)

ser = serial.Serial('/dev/ttyUSB0',9600, timeout=1)
ser.reset_input_buffer()

write_serial_string(ser, "ON")

wait_serial_string(ser, "IT")

iteration = int(read_serial_string(ser))

client = tago.Device(credentials.tagoToken)
filename = '/home/pi/v2_prototype/number.txt'

last_curr = last_total = 0 #with no file, all will to ZERO
with open(filename, 'r') as f:
    line = f.readlines()[-1] #read the last line
    last_curr, last_total = map(int, line.split("/"))

if(iteration > last_curr):#alway TRUE, else error
    if iteration > last_curr: #is the same battery, just write
        with open(filename, "a") as f: f.write("%s/%s\n"%(iteration, last_total))#append at the last line

    else: #is a new battery, update the total
        last_total = last_curr
        with open(filename, "w") as f: f.write("%s/%s\n"%(iteration, last_total))#new file
    
    if last_total > 0:
        battery = 100-((iteration*100.0)/last_total)
    else:
        battery = 100-((iteration*100.0)/10000)#just for calibration
    

    data = {
        'variable': 'bateria',
        'value': str(battery),
        'unit': '%'
    }

    client.insert(data)

    raspFunctions.obtainTemperature(client)
    camera = PiCamera()
    raspFunctions.runModelFCN(client, camera, xCut, yCut, point)
    camera.close()
    #time.sleep(timeToMeasure)

    #write_serial_string(ser, "SHUT")
    

else:
    print("ERROR")

