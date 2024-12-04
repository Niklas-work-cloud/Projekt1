import RPi.GPIO as GPIO
import time

# GPIO Setup
LIGHT_PIN = 17
PUMP_PIN = 27
FAN_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_PIN, GPIO.OUT)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)

# Testgeräte ein- und ausschalten
GPIO.output(LIGHT_PIN, GPIO.HIGH)  # Licht an
time.sleep(2)                     # 2 Sekunden warten
GPIO.output(LIGHT_PIN, GPIO.LOW)   # Licht aus

GPIO.output(PUMP_PIN, GPIO.HIGH)   # Pumpe an
time.sleep(2)
GPIO.output(PUMP_PIN, GPIO.LOW)    # Pumpe aus

GPIO.output(FAN_PIN, GPIO.HIGH)    # Ventilator an
time.sleep(2)
GPIO.output(FAN_PIN, GPIO.LOW)     # Ventilator aus

GPIO.cleanup()  # Pins zurücksetzen
