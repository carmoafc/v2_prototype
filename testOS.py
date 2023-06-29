import os
import subprocess

a = os.system("/opt/vc/bin/vcgencmd measure_temp")
print(a)

output = subprocess.check_output('/opt/vc/bin/vcgencmd measure_temp', shell=True, text=True)
temperature_str = output.strip().split("=")[1]
temperature_float = float(temperature_str.split("'")[0])

print("CPU Temperature:", temperature_float, "°C")
