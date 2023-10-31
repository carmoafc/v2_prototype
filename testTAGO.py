import tago
import credentials
import json

# Cria uma instância do dispositivo Tago
device = tago.Device(credentials.tagoToken)

filter = {
'variable': 'email',
'query': 'last_value',
'end_date': '2023-12-25 23:33:22',
'start_date': '2014-12-20 23:33:22'
}

result = device.find(filter)
print(result)

valor_result = result.get('result')

print(valor_result)