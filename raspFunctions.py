def takePhotoFCN():
    print('')

def takeVideoFCN():
    print('')

def updateModelFCN():
    import os
    os.system('wget https://github.com/clodoaldocodes/v2_prototype/blob/main/Model-_1.tflite')

def calibrateFCN():
    print('')

def on_message(message):
    print("message received: " + str(message))

    if message.channel==6:
        breakAllFCN()

def runModelFCN(should_stop):
    from tflite_runtime.interpreter import Interpreter
    from PIL import Image
    import numpy as np
    import time
    import cayenne.client
    import credentials
    import datetime

    tflite_model_path = '/home/pi/v2_prototype/Model-_1.tflite'
    interpreter = Interpreter(tflite_model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]['shape']
    size = input_shape[1:3]

    typeWater = ['limpa', 'nada', 'suja']
    filename = '/home/pi/v2_prototype/nada_0_18.jpg'

    client = cayenne.client.CayenneMQTTClient()
    client.on_message = on_message
    client.begin(credentials.MQTT_USERNAME, credentials.MQTT_PASSWORD, credentials.MQTT_CLIENT_ID, port = 8883)

    while not should_stop:
        client.loop()
        img = Image.open(filename).convert('RGB') #read the image and convert it to RGB format
        img = img.resize(size) #resize the image to 224x224
        img = np.array(img) # convert the image in an array
        processed_image = np.expand_dims(img, axis=0)# Add a batch dimension
        processed_image = np.array(processed_image, dtype='float32')

        # Now allocate tensors so that we can use the set_tensor() method to feed the processed_image
        interpreter.allocate_tensors()
        #print(input_details[0]['index'])
        interpreter.set_tensor(input_details[0]['index'], processed_image)

        t1=time.time()
        interpreter.invoke()
        t2=time.time() 
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        index = np.argmax(predictions)   
        
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]) + ' - Predict: ' + typeWater[index])

        client.virtualWrite(0, int(index))

        time.sleep(2)

# def breakAllFCN():
#     return 1