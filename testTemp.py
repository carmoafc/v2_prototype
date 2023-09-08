# import subprocess

# output = subprocess.check_output('/usr/bin/vcgencmd measure_temp', shell=True, text=True, stderr=subprocess.PIPE)
# temperature_str = output.strip().split("=")[1]
# temperature_float = float(temperature_str.split("'")[0])
# # print(temperature_float)

import tago

my_device = tago.Device('5a6f3079-c251-4b5b-aeee-87ad36e5c420')

"""
The following code defines the set of data to be sent to TagoIO
data fields:
- variable name
- variable unit
- variable value
- Optional: desired data timestamp 
- Optional: lat/long location (associated to your data) 
"""
data = {
            'variable': 'estadoagua',                                                  
            'value'   : 'Nada',                                                                    
}

result = my_device.insert(data)

data1 = {
    'variable': 'bateria',
    'value': str(10),
    'unit': '%'
}

result = my_device.insert(data1)