from picamera import PiCamera
import time

camera = PiCamera()

camera.start_preview()
time.sleep(20)
camera.capture('/home/pi/v2_prototype/image.jpg')
camera.stop_preview()
print('Finished')