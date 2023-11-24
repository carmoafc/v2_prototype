import subprocess
import time

comando_bash = "sudo openvpn --config /home/pi/v2_prototype/vpn_inspectral.ovpn --daemon"
subprocess.run(comando_bash, shell=True)

time.sleep(5)

comando_bash = "hostname -I"
processo = subprocess.Popen(comando_bash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
saida, erro = processo.communicate()
print("Saída do comando:", saida)
print("Código de retorno:", processo.returncode)

comando_bash = "sudo pkill openvpn"
subprocess.run(comando_bash, shell=True)

comando_bash = "sudo ip link delete tun0"
subprocess.run(comando_bash, shell=True)

'''bash_command = "hostname -I"
process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
output, error = process.communicate()
print("Command output:", output)
print("Return code:", process.returncode)'''