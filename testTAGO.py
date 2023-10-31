import tago
import credentials
import ast

# Cria uma instância do dispositivo Tago
device = tago.Device(credentials.tagoToken)

# Recupera os últimos valores da variável
json_data = device.find({'variable': "email"})

# Converte a string para um dicionário Python usando ast.literal_eval
data_dict = ast.literal_eval(json_data)

# Obtém o primeiro e-mail recebido
primeiro_email = data_dict['result'][0]['value']

# Imprime o primeiro e-mail
print(f"O primeiro e-mail recebido é: {primeiro_email}")