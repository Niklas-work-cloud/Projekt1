import RPi.GPIO as GPIO
import spidev
import time
import Adafruit_DHT  # DHT-Sensor-Bibliothek

# GPIO-Pin-Konfiguration
LIGHT_PIN = 17
PUMP_PIN = 27
FAN_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_PIN, GPIO.OUT)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)

# MCP3008 Setup für SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Gerät 0
spi.max_speed_hz = 1000000

# DHT Sensor Konfiguration
DHT_SENSOR = Adafruit_DHT.DHT22  # DHT11 oder DHT22
DHT_PIN = 4  # GPIO-Pin, an dem der DHT-Sensor angeschlossen ist

# Hilfsfunktionen zur Erfassung von Sensordaten
def read_adc(channel):
    if channel > 7 or channel < 0:
        raise ValueError("ADC Channel must be between 0 and 7")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def get_soil_moisture():
    soil_value = read_adc(0)  # Kanal 0 ist für Bodenfeuchtigkeit
    return (soil_value / 1023.0) * 100

def get_water_level():
    water_value = read_adc(1)  # Kanal 1 ist für den Wasserstand
    return (water_value / 1023.0) * 100

def get_temperature_humidity():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return round(temperature, 2), round(humidity, 2)
    else:
        print("Fehler beim Auslesen des DHT-Sensors")
        return None, None

# Steuerungsfunktionen für die Aktuatoren
def control_device(component, action):
    pin = {"light": LIGHT_PIN, "pump": PUMP_PIN, "fan": FAN_PIN}.get(component)
    if pin:
        GPIO.output(pin, GPIO.HIGH if action == "on" else GPIO.LOW)
        print(f"{component} wurde {action} geschaltet.")

# Testen der Sensoren und Aktuatoren
def test_sensors_and_activators():
    # Sensorwerte ablesen
    soil_moisture = get_soil_moisture()
    water_level = get_water_level()
    temperature, humidity = get_temperature_humidity()

    # Sensorwerte anzeigen
    print(f"Bodenfeuchtigkeit: {soil_moisture:.2f}%")
    print(f"Wasserstand: {water_level:.2f}%")
    print(f"Temperatur: {temperature}°C")
    print(f"Luftfeuchtigkeit: {humidity}%")

    # Aktuatoren steuern (beispielhafte Steuerung)
    print("\nAktuatoren Test:")
    
    # Licht steuern
    control_device("light", "on")  # Licht einschalten
    time.sleep(2)
    control_device("light", "off")  # Licht ausschalten
    time.sleep(1)
    
    # Pumpe steuern
    control_device("pump", "on")  # Pumpe einschalten
    time.sleep(2)
    control_device("pump", "off")  # Pumpe ausschalten
    time.sleep(1)
    
    # Ventilator steuern
    control_device("fan", "on")  # Ventilator einschalten
    time.sleep(2)
    control_device("fan", "off")  # Ventilator ausschalten
    time.sleep(1)

if __name__ == "__main__":
    try:
        test_sensors_and_activators()  # Testen der Sensoren und Aktuatoren
    except KeyboardInterrupt:
        print("Programm wurde beendet.")
    finally:
        GPIO.cleanup()  # GPIO sauber zurücksetzen
