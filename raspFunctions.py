def takePhotoFCN(camera):
    import time

    time.sleep(5)
    camera.capture('/home/pi/v2_prototype/image.jpg')
    return None

def takeVideoFCN(camera):
    import time

    camera.start_recording('/home/pi/v2_prototype/desiredfilename.h264')
    time.sleep(5)
    camera.stop_recording()
    return None

def updateModelFCN():
    import os
    os.system('wget -0 /home/pi/v2_prototype/Model-_1.tflite https://github.com/clodoaldocodes/v2_prototype/blob/main/Model-_1.tflite')
    return None

def calibrateFCN():
    import cv2
    import os
    
    os.system('wget -O /home/pi/v2_prototype/drive_img.png https://github.com/clodoaldocodes/v2_prototype/blob/main/drive_img.png')
    image = cv2.imread('/home/pi/v2_prototype/drive_img.png')
    lower_red = (0, 0, 210)
    upper_red = (50, 50, 255)

    mask = cv2.inRange(image, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        print(cv2.contourArea(contour))
        if cv2.contourArea(contour) > 0: 
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    xCut = [x, x+w]
    yCut = [y, y+h]
    return xCut, yCut

def on_message(message):
    print("message received: " + str(message))
    return None

def sendEmail(value):  
    import datetime
    import smtplib
    import email.message
    import credentials

    typeWater = ['clean', 'nothing', 'dirty']

    bodyEmail = \
    '<h1>Water quality alert</h1>' + \
    '<h2>Date: ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + \
    '</h2><p>The water quality in this time is <b>' + \
    typeWater[value] + '</b></p>' + \
    '<p>Please go to point X and check what is happening.</p>' + \
    '<p>Any error that may occur send an email to XXXX@gmail.com</p>'
    
    msg = email.message.Message()
    msg['Subject'] = "WATER QUALITY ALERT!!"
    msg['From'] = credentials.email
    msg['To'] = 'cdsfj@hotmail.com'
    password = credentials.passwordAPI
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(bodyEmail)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')

    return None

def runModelFCN(client, camera, xCut, yCut):
    from tflite_runtime.interpreter import Interpreter
    from PIL import Image
    import numpy as np
    import time
    import cayenne.client
    import credentials
    import datetime
    from picamera import PiCamera

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
    sendEmail(int(index))
    
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + ' - Predict: ' + typeWater[index])

    client.virtualWrite(0, int(index))

    time.sleep(2)
    return None

# def breakAllFCN():
#     return 1

def reboot():
    import subprocess
    subprocess.call('sudo reboot', shell=True)
    return None