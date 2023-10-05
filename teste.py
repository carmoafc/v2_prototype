import RPi.GPIO as GPIO
import time

# Configurar o pino GPIO 21 para entrada
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)
GPIO.setup(20, GPIO.OUT)

times = 5
try:
    while True:
        # Ler o estado do pino GPIO 21
        gpio_state = GPIO.input(21)
        print(f"Estado do GPIO 21: {gpio_state}")

        time.sleep(times)  # Aguardar 1 segundo antes de ler novamente

        # Enviar um sinal de alto (HIGH)
        GPIO.output(20, GPIO.HIGH)
        print("Sinal de alto enviado para o GPIO 20")

        time.sleep(times)

        GPIO.output(20, GPIO.LOW)
        print("Sinal de baixo enviado para o GPIO 20")
except KeyboardInterrupt:
    # Tratamento para encerrar o programa com Ctrl+C
    GPIO.cleanup()
