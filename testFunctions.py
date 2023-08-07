# import raspFunctions
# from picamera import PiCamera

# camera = PiCamera()
# raspFunctions.takePhotoFCN(camera)

from tflite_runtime.interpreter import Interpreter
from PIL import Image
import numpy as np
import time
import cayenne.client
import credentials
import datetime
from picamera import PiCamera
import cv2

xCut = [0, 256]
yCut = [0, 256]
camera = PiCamera()

tflite_model_path = '/home/pi/v2_prototype/Model-_1.tflite'
interpreter = Interpreter(tflite_model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']
size = input_shape[1:3]

typeWater = ['clean', 'nothing', 'dirty']

time.sleep(1)
filename = '/home/pi/v2_prototype/image.jpg'

camera.capture(filename)

img = Image.open(filename).convert('RGB') #read the image and convert it to RGB format
img = img.resize(size) #resize the image to 224x224
img = np.array(img) # convert the image in an array
if xCut[1] != 0:
    img = img[yCut[0]:yCut[1], xCut[0]:xCut[1]]

processed_image = np.expand_dims(img, axis=0)# Add a batch dimension
processed_image = np.array(processed_image, dtype='float32')

# Now allocate tensors so that we can use the set_tensor() method to feed the processed_image
interpreter.allocate_tensors()
#print(input_details[0]['index'])
interpreter.set_tensor(input_details[0]['index'], processed_image)

# t1=time.time()
interpreter.invoke()
# t2=time.time() 
predictions = interpreter.get_tensor(output_details[0]['index'])[0]
index = np.argmax(predictions)  

print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + ' - Predict: ' + typeWater[index])