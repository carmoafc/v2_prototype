import boto3
import credentials

# Configure AWS credentials
aws_access_key_id = 
aws_secret_access_key = 'YOUR_SECRET_KEY'
aws_session_token = 'YOUR_SESSION_TOKEN'  # Optional for temporary credentials

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)

bucket_name = 'your-s3-bucket-name'
file_path = 'path/to/your/file.ext'  # Path to the file you want to upload
s3_key = 'path/in-s3/bucket/file.ext'  # The key (path) under which the file will be stored in S3

s3.upload_file(file_path, bucket_name, s3_key)