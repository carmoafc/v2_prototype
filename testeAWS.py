import boto3
import credentials

# Substitua essas informações pelas suas próprias credenciais e nome do bucket
aws_access_key_id = credentials.aws_access_key_id
aws_secret_access_key = credentials.aws_secret_access_key
aws_bucket_name = credentials.aws_buket_name

# Nome do arquivo local que você deseja enviar
local_file_path = '/home/pi/v2_prototype/A_small_cup_of_coffee.JPG'

# Nome do arquivo no bucket da AWS
s3_file_key = 'a'

# Cria uma instância do cliente S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Faz o upload do arquivo para o bucket da AWS
s3.upload_file(local_file_path, aws_bucket_name, s3_file_key)

print(f'A imagem foi enviada para o bucket {aws_bucket_name} com sucesso.')