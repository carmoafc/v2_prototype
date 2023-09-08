from gpiozero import DigitalInputDevice
import os

pinNumber = 4
input = DigitalInputDevice(pinNumber)
filename = 'number.txt'

if input.value:
    with open(filename, 'w') as file:
            file.write(str(0))
    
    os.system('git clone https://github.com/clodoaldocodes/v2_prototype')