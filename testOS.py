# import os
# import subprocess

# a = os.system("/opt/vc/bin/vcgencmd measure_temp")
# print(a)

# output = subprocess.check_output('/opt/vc/bin/vcgencmd measure_temp', shell=True, text=True)
# temperature_str = output.strip().split("=")[1]
# temperature_float = float(temperature_str.split("'")[0])

# print("CPU Temperature:", temperature_float, "°C")


# import time
# from picamera import PiCamera

# camera = PiCamera()

# time.sleep(5)
# camera.capture('/home/pi/v2_prototype/image.jpg')

import cv2

img = cv2.imread('/home/pi/v2_prototype/drive_img.png')
#hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lower_red = (0, 0, 210)
upper_red = (50, 50, 255) #BGR

mask = cv2.inRange(img, lower_red, upper_red)

contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    
    print(cv2.contourArea(contour))
    if cv2.contourArea(contour) > 0: 
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

xCut = [x, x+w]
yCut = [y, y+h]

print(xCut)
print(yCut)