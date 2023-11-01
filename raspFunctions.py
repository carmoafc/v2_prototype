import os
import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import credentials
import numpy as np

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
    os.system('rm -f /home/pi/v2_prototype/Model-_1.tflite')
    os.system('wget https://github.com/clodoaldocodes/v2_prototype/raw/main/Model-_1.tflite -P /home/pi/v2_prototype')
    return None

def calibrateFCN():
    import cv2
    import os
    
    os.system('rm -f /home/pi/v2_prototype/drive_img.png')
    os.system('wget https://github.com/clodoaldocodes/v2_prototype/raw/main/drive_img.png -P /home/pi/v2_prototype')

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

def sendEmail(value, point):  
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from PIL import Image
    import credentials

    typeWater = ['Limpa', 'SemAgua', 'Suja']
    imagePath = '/home/pi/v2_prototype/'  
    filename = 'image.jpg' 

    imagePath = os.path.join(imagePath, filename)

    maxWidth = 640
    with Image.open(imagePath) as image:
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image.thumbnail((maxWidth, maxWidth))
        tempImagePath = imagePath + 'temp.jpg'
        image.save(tempImagePath)

    bodyEmail = \
        '<h1>Alerta do protótipo </h1>' + \
        '<h2>Hora: ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + \
        '</h2><p>A água foi classificada como <b>' + \
        typeWater[value] + '</b></p>' + \
        '<p>Se dirija ao ponto ' + point + ' e verifique o que está acontecendo.</p>' + \
        '<p>Qualquer erro que venha a ocorrer, entre em contato com team@inspectral.com</p>' + \
        '<p>Imagem que foi obtida da região observada: </p>' + \
        '<img src="cid:image1">'  

    msg = MIMEMultipart()
    msg['Subject'] = "ALERTA DO PROTÓTIPO!!"
    msg['From'] = credentials.email
    msg['To'] = credentials.emailTo
    password = credentials.passwordAPI

    body = MIMEText(bodyEmail, 'html')
    msg.attach(body)

    with open(tempImagePath, 'rb') as image_file:
        image_data = image_file.read()
    imagePart = MIMEImage(image_data, name=os.path.basename(imagePath))
    imagePart.add_header('Content-ID', '<image1>')
    imagePart.add_header("Content-Disposition", "inline", filename=os.path.basename(imagePath))
    msg.attach(imagePart)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

    os.remove(tempImagePath)
    print('Email enviado')
    return None

def runModelFCN(client, camera, xCut, yCut, point):
    from tflite_runtime.interpreter import Interpreter
    from PIL import Image
    import numpy as np
    import time
    from picamera import PiCamera

    tflite_model_path = '/home/pi/v2_prototype/Model-_1.tflite'
    interpreter = Interpreter(tflite_model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]['shape']
    size = input_shape[1:3]

    typeWater = ['Limpa', 'SemAgua', 'Suja']

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
    if int(index) == 2:
        sendEmail(int(index), point)    
    
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + ' - Predict: ' + typeWater[index])

    data = {
            'variable': 'estadoagua',                                                  
            'value'   : typeWater[index],                                                                    
    }

    client.insert(data)

    time.sleep(2)
    return typeWater[index]

def reboot():
    import subprocess
    subprocess.call('sudo reboot', shell=True)
    return None

def obtainTemperature(client):
    import subprocess

    output = subprocess.check_output('/usr/bin/vcgencmd measure_temp', shell=True, text=True, stderr=subprocess.PIPE)
    temperature_str = output.strip().split("=")[1]
    temperature_float = float(temperature_str.split("'")[0])
    data = {
            'variable': 'temperatura',                                                  
            'value'   : str(temperature_float),
            'unit'    : 'ºC'                                                                    
    }

    client.insert(data)

    return None

def sendMensage(client, channel, value):
    client.virtualWrite(channel, value)

def download_git():
    import os
    import requests

    # Caminho local do arquivo
    caminho_local = '/home/pi/v2_prototype/Model-_1.tflite'

    # Remover o arquivo existente, se houver
    if os.path.exists(caminho_local):
        os.remove(caminho_local)
        print(f"Arquivo existente removido: {caminho_local}")

    # URL do arquivo no GitHub
    url_arquivo_github = 'https://github.com/clodoaldocodes/v2_prototype/raw/main/Model-_1.tflite'

    # Baixar o arquivo
    try:
        resposta = requests.get(url_arquivo_github)
        resposta.raise_for_status()  # Verificar se houve um erro na solicitação

        # Verificar se o conteúdo é válido
        if 'Model provided has model identifier' in resposta.text:
            print("Erro: O arquivo baixado parece conter um erro. Verifique o conteúdo do arquivo no GitHub.")
        else:
            # Salvar o conteúdo do arquivo
            with open(caminho_local, 'wb') as arquivo_local:
                arquivo_local.write(resposta.content)

            print(f"Arquivo baixado com sucesso para: {caminho_local}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")

def write_date_to_file(date, file_name="/home/pi/v2_prototype/data_send.txt"):
    with open(file_name, 'w') as file:
        file.write(date)

def read_date_from_file(file_name="/home/pi/v2_prototype/data_send.txt"):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            date_str = file.read().strip()
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                return date
            except ValueError:
                print("Invalid date format in the file.")
                return None
    else:
        print(f"The file {file_name} does not exist.")
        return None

def compare_and_replace_date(file_name="/home/pi/v2_prototype/data_send.txt"):
    current_date = datetime.datetime.now()
    previous_date = read_date_from_file(file_name)
    
    if previous_date is None or current_date > previous_date:
        write_date_to_file(current_date.strftime('%Y-%m-%d'), file_name)
        print("Date replaced successfully.")
        return True
    else:
        print("The current date is not greater than the existing date in the file.")
        return False

def send_report(client, textFilePath):

    filter = {
    'variable': 'email',
    'end_date': '2023-12-25 23:33:22',
    'start_date': '2014-12-20 23:33:22'
    }

    result = client.find(filter)
    valor_result = result.get('result')

    email_to_send = []
    for i in range(len(valor_result)):
        email_value = valor_result[i].get('value') if valor_result else None
        #print(email_value)
        email_to_send.append(email_value)

    #print(email_to_send)
    email_to_send = np.unique(email_to_send)

    bodyEmail = \
        '<h1>Relatório das medições:  </h1>' + \
        '<p> </p>' + \
        '<pre>' + open(textFilePath).read() + '</pre>'

    current_date = datetime.datetime.now()
    str_date = current_date.strftime("%Y-%m-%d")
    name_email = "RELATÓRIO - PROTÓTIPO - " + str_date
    for i in range(len(email_to_send)):
        msg = MIMEMultipart()

        msg['Subject'] = name_email
        msg['From'] = credentials.email

        msg['To'] = email_to_send[i]
        password = credentials.passwordAPI

        body = MIMEText(bodyEmail, 'html')
        msg.attach(body)

        with open(textFilePath, 'rb') as text_file:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(text_file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=textFilePath)
            msg.attach(attachment)

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

        print('Email enviado para ' + email_to_send[i])
