import raspFunctions

result = raspFunctions.compare_and_replace_date()
print(result)

filename = "/home/pi/v2_prototype/data_send.txt"
if result:
    with open(filename, "a") as file:
            file.write("A - " + str(0) + "\n")
else:
    with open(filename, "w") as file:
            file.write("A - " + str(0) + "\n")



import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import credentials

typeWater = ['Limpa', 'SemAgua', 'Suja']
textFilePath = '/home/pi/v2_prototype/data_send.txt'
filename = 'data_send.txt'

value = 0
point = "alpha"

bodyEmail = \
    '<h1>Alerta do protótipo </h1>' + \
    '<h2>Hora: ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]) + \
    '</h2><p>A água foi classificada como <b>' + \
    typeWater[value] + '</b></p>' + \
    '<p>Se dirija ao ponto ' + point + ' e verifique o que está acontecendo.</p>' + \
    '<p>Qualquer erro que venha a ocorrer, entre em contato com team@inspectral.com</p>' + \
    '<p>Relatório das medições: </p>' + \
    '<p> </p>' + \
    '<pre>' + open(textFilePath).read() + '</pre>'

msg = MIMEMultipart()
msg['Subject'] = "ALERTA DO PROTÓTIPO!!"
msg['From'] = credentials.email
msg['To'] = credentials.emailTo
password = credentials.passwordAPI

body = MIMEText(bodyEmail, 'html')
msg.attach(body)

with open(textFilePath, 'rb') as text_file:
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(text_file.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(attachment)

s = smtplib.SMTP('smtp.gmail.com: 587')
s.starttls()
s.login(msg['From'], password)
s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

print('Email enviado')

