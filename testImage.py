from PIL import Image
import os

imagePath = '/home/pi/v2_prototype/'  
filename = 'image.jpg' 
imagePath2 = os.path.join(imagePath, filename)

maxWidth = 640
with Image.open(imagePath2) as image:
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    image.thumbnail((maxWidth, maxWidth))
    tempImagePath = imagePath + 'temp.jpg'
    image.save(tempImagePath)

with open(tempImagePath, 'rb') as image_file:
    image_data = image_file.read()


