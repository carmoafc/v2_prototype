import subprocess

output = subprocess.check_output('/usr/bin/vcgencmd measure_temp', shell=True, text=True, stderr=subprocess.PIPE)
temperature_str = output.strip().split("=")[1]
temperature_float = float(temperature_str.split("'")[0])
print(temperature_float)