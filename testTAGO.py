import tago
import credentials
import json
import numpy as np

# Cria uma instância do dispositivo Tago
device = tago.Device(credentials.tagoToken)

filter = {
'variable': 'email',
'end_date': '2023-12-25 23:33:22',
'start_date': '2014-12-20 23:33:22'
}

result = device.find(filter)
valor_result = result.get('result')

# Extrair o valor associado à chave 'value' na lista
email_to_send = []
for i in range(len(valor_result)):
    email_value = valor_result[i].get('value') if valor_result else None
    print(email_value)
    email_to_send.append(email_value)

print(email_to_send)
email_to_send = np.unique(email_to_send)

print("----------------")
print(email_to_send)
