import requests

url='http://www.google.com/'
timeout=3
r = requests.head(url, timeout=timeout)

print(r)