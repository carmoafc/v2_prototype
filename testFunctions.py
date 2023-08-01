import raspFunctions
from picamera import PiCamera

camera = PiCamera()
raspFunctions.takePhotoFCN(camera)