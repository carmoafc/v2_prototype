from tago import Tago

# Substitua com suas credenciais e informações do dispositivo no Tago
TAGO_TOKEN = 'd0064505-d433-4d6f-a676-79233141f249'
DEVICE_ID = '64fb28b4801f850010f7a311'  # Substitua pelo ID real do seu dispositivo

# Caminho da imagem que você deseja enviar
image_path = "D:/v2_prototype/A_small_cup_of_coffee.JPG"

# Função para converter uma imagem em Base64
def image_to_base64(file_path):
    with open(file_path, 'rb') as image_file:
        return image_file.read().encode('base64').decode('utf-8')

# Convertendo a imagem em Base64
image_base64 = image_to_base64(image_path)

# Inicializando a instância do Tago com o token
tago_device = Tago(token=TAGO_TOKEN)

# Enviando dados para o Tago
tago_device.insert(DEVICE_ID, {
    'variable': 'image_data',
    'value': image_base64,
})

print('Dados enviados com sucesso para o Tago.')
