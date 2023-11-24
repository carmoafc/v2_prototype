import os
import time
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import credentials
import numpy as np
import boto3
import uuid
import cv2 
from PIL import Image
from tflite_runtime.interpreter import Interpreter
from picamera import PiCamera
import subprocess
import requests

def takePhotoFCN(camera):

    time.sleep(5)
    camera.capture('/home/pi/v2_prototype/image.jpg')
    return None

def takeVideoFCN(camera):

    camera.start_recording('/home/pi/v2_prototype/desiredfilename.h264')
    time.sleep(5)
    camera.stop_recording()
    return None

def updateModelFCN():

    os.system('rm -f /home/pi/v2_prototype/Model-_1.tflite')
    os.system('wget https://github.com/clodoaldocodes/v2_prototype/raw/main/Model-_1.tflite -P /home/pi/v2_prototype')
    return None

def calibrateFCN():

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

def sendEmail(client, value, point):  
    typeWater = ['Limpa', 'SemAgua', 'Suja']
    imagePath = '/home/pi/v2_prototype/'  
    filename = 'image.jpg' 

    email_to_send = choose_emails_send(client)

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

    for i in range(len(email_to_send)):
        msg = MIMEMultipart()
        msg['Subject'] = "ALERTA DO PROTÓTIPO!!"
        msg['From'] = credentials.email
        msg['To'] = email_to_send[i]
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

        print('Email enviado para ' + email_to_send[i])
    os.remove(tempImagePath)
    return None

def runModelFCN(client, camera, xCut, yCut, point):

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

    img = cv2.imread(filename)
    img_cw_180 = cv2.rotate(img, cv2.ROTATE_180)
    cv2.imwrite(filename, img_cw_180)

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
        sendEmail(client, int(index), point)    
    
    print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + ' - Predict: ' + typeWater[index])

    '''data = {
            'variable': 'estadoagua',                                                  
            'value'   : typeWater[index],                                                                    
    }

    client.insert(data)'''

    time.sleep(2)
    url = sendToAws(index)

    data2 = {
                'variable': 'url',                                                  
                'value'   : url,                                                                    
    }

    client.insert(data2)

    return typeWater[index]

def reboot():
    
    subprocess.call('sudo reboot', shell=True)
    return None

def obtainTemperature():

    output = subprocess.check_output('/usr/bin/vcgencmd measure_temp', shell=True, text=True, stderr=subprocess.PIPE)
    temperature_str = output.strip().split("=")[1]
    temperature_float = float(temperature_str.split("'")[0])

    return temperature_float

def sendMensage(client, channel, value):

    client.virtualWrite(channel, value)

def download_git(client):

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
        msg = "Erro ao baixar o arquivo"
        print(f"{msg}: {e}")
        send_log(client, option=8, msg_personalize=msg)

def write_date_to_file(date, file_name="/home/pi/v2_prototype/data.txt"):
    with open(file_name, 'w') as file:
        file.write(date)

def read_date_from_file(file_name="/home/pi/v2_prototype/data.txt"):
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

def compare_and_replace_date(file_name="/home/pi/v2_prototype/data.txt"):
    current_date = datetime.datetime.now()
    previous_date = read_date_from_file(file_name)
    
    if previous_date is None or current_date > previous_date + datetime.timedelta(days=10):
        write_date_to_file(current_date.strftime('%Y-%m-%d'), file_name)
        print("Date replaced successfully.")
        return True
    else:
        print("The current date is not greater than the existing date in the file.")
        return False

def send_report(client, textFilePath):
    email_to_send = choose_emails_send(client)

    bodyEmail = \
        '<h1>Relatório das medições:  </h1>' + \
        '<p> </p>' + \
        '<pre>' + open(textFilePath).read() + '</pre>'

    current_date = datetime.datetime.now()
    str_date = current_date.strftime("%Y_%m_%d")
    name_email = "RELATÓRIO - PROTÓTIPO - " + str_date
    for i in range(len(email_to_send)):
        msg = MIMEMultipart()

        msg['Subject'] = name_email
        msg['From'] = credentials.email

        msg['To'] = email_to_send[i]
        password = credentials.passwordAPI

        body = MIMEText(bodyEmail, 'html')
        msg.attach(body)

        name_txt = "report_" + str_date + ".txt"
        with open(textFilePath, 'rb') as text_file:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(text_file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=name_txt)
            msg.attach(attachment)

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

        print('Email enviado para ' + email_to_send[i])

    return None

def sendToAws(value):
    typeWater = ['Limpa', 'SemAgua', 'Suja']
    aws_access_key_id = credentials.aws_access_key_id
    aws_secret_access_key = credentials.aws_secret_access_key
    aws_bucket_name = credentials.aws_buket_name

    guid_uuid4 = uuid.uuid4()

    # Nome do arquivo local que você deseja enviar
    local_file_path = '/home/pi/v2_prototype/image.jpg'

    # Nome do arquivo no bucket da AWS
    s3_file_key =  str(guid_uuid4) + '/' + typeWater[value] + '.jpg'

    # Cria uma instância do cliente S3
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Faz o upload do arquivo para o bucket da AWS
    s3.upload_file(local_file_path, aws_bucket_name, s3_file_key)

    print(f'A imagem foi enviada para o bucket {aws_bucket_name} com sucesso.')

    url =  aws_bucket_name + ".s3.amazonaws.com/" + s3_file_key
    return url

def choose_emails_send(client):
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

    return email_to_send

def send_log(client, option, msg_personalize=None):
    current_date = datetime.datetime.now()
    str_date = current_date.strftime("%d-%m-%Y %H:%M")

    if option==1:
        msg = "Dispositivo conectado"
    if option==2:
        msg = "Capturando imagem para processamento"
    if option==3:
        msg = "Processamento concluído"
    if option==4:
        msg = "Processo finalizado"
    if option==5:
        msg = "Unidade de processamento desligando"
    if option==6:
        msg = "Atualizando modelo de IA"
    if option==7:
        msg = "Relatório enviado nos e-mails"
    if option==8:
        msg = "IP: " + msg_personalize
    if option==0:
        msg = "Unidade de processamento iniciando"
    
    data = [
        {"variable": "log",
        "value": msg},
        {"variable": "date",
        "value": str_date}
    ]
    client.insert(data)
    return None

def send_log_monitoring(client, index, battery, temperature):
    current_date = datetime.datetime.now()
    str_date = current_date.strftime("%d-%m-%Y %H:%M")
    
    data = [
    {
        "variable": "bateria",
        "value": str(round(battery,1)),
        "unit": "%"
    },
    {
        "variable": "temperatura",
        "value": str(temperature),
        "unit": "ºC"
    },
    {
        "variable": "date_monitoring",
        "value": str_date,
    },
    {
        "variable": "estadoagua",
        "value": index,
    }
    ]

    client.insert(data)
    return None

def conect_vpn():
    # Command to start OpenVPN in daemon mode
    bash_command = "sudo openvpn --config vpn_inspectral_vpn.ovpn --daemon"
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    #print("Command output:", output)
    #print("Return code:", process.returncode)

    # Command to get the IP address of the host
    bash_command = "hostname -I"
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    #print("Command output:", output)
    #print("Return code:", process.returncode)
    return output

def disconect_vpn():
    bash_command = "sudo pkill openvpn"
    subprocess.run(bash_command, shell=True)

    bash_command = "sudo ip delete link tun0"
    subprocess.run(bash_command, shell=True)

    return None