import requests
import base64
import credentials

# Substitua com suas credenciais e informações do dispositivo no Tago
TAGO_TOKEN = "d0064505-d433-4d6f-a676-79233141f249"
DEVICE_ID = "64fb28b4801f850010f7a311"

# Caminho da imagem que você deseja enviar
image_path = "D:/v2_prototype/A_small_cup_of_coffee.JPG"

# Função para converter uma imagem em Base64
def image_to_base64(file_path):
    with open(file_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Convertendo a imagem em Base64
image_base64 = image_to_base64(image_path)

# Dados a serem enviados para o Tago
data_to_send = {
    'variable': 'image_data',
    'value': image_base64,
}

# URL da API do Tago para enviar dados
api_url = f'https://api.tago.io/data/{DEVICE_ID}'

# Configurações da requisição para a API do Tago
headers = {
    'Content-Type': 'application/json',
    'Device-Token': TAGO_TOKEN,
}

# Enviando os dados para o Tago
response = requests.post(api_url, json=data_to_send, headers=headers)

# Exibindo informações de debug
print('Status Code:', response.status_code)
print('Response Text:', response.text)

# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    print('Dados enviados com sucesso para o Tago:', response.json())
else:
    print('Erro ao enviar dados para o Tago. Verifique as mensagens de debug acima.')