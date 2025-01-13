from flask import Flask, jsonify, request
from flask_cors import CORS
import RPi.GPIO as GPIO
import spidev
import time
from datetime import datetime
import logging
from threading import Thread
import requests  # Zum Senden der Daten an die API

app = Flask(__name__)
CORS(app)

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# GPIO-Pin-Konfiguration
LIGHT_PIN = 19
PUMP_PIN = 26
FAN_PIN = 13

#GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_PIN, GPIO.OUT)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)

# MCP3008 Setup für SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Gerät 0
spi.max_speed_hz = 1000000

# Globale Variablen für Zeitpläne und manuelle Steuerung
schedule = {
    "light": {"start": "06:00", "end": "18:00"},
    "pump": {"start": "06:00", "end": "18:00"},
    "fan": {"start": "06:00", "end": "18:00"},
    "fan_interval": 30,  # Minuten
    "fan_duration": 5,   # Minuten
}

manual_control = {
    "light": False,
    "pump": False,
    "fan": False
}  # Steuert manuell die Geräte

# Hilfsfunktionen zur Erfassung von Sensordaten
def read_adc(channel):
    if channel > 7 or channel < 0:
        raise ValueError("ADC Channel must be between 0 and 7")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def get_soil_moisture():
    soil_value = read_adc(0)  # Kanal 0 ist für Bodenfeuchtigkeit
    if soil_value > 700:
        return 0
    elif soil_value < 310:
        return 100
    else:
        # Linear interpolieren, um den Wert zwischen 0% und 100% zu berechnen
        return ((700 - soil_value) / (700 - 310)) * 100
    
def get_water_level():
    water_value = read_adc(1)  # Kanal 1 ist für den Wasserstand
    if water_value < 0:
        return 0
    elif water_value > 600:
        return 100
    else:
        return (water_value / 600.0) * 100
    
def get_power_consumption():
    adc_value = read_adc(2)  # Kanal 2 für den ACS712 am MCP3008
    
    # Umrechnung des ADC-Werts in eine Spannung (0-5V)
    voltage = (adc_value / 1023.0) * 5.0
    
    # Berechnung des Stroms in Ampere (ACS712-05B, Sensitivität: 185 mV/A)
    current_in_amps = (voltage - 2.5) / 0.185  # Offset bei 2.5V
    
    # Strombegrenzung für Mapping: maximal 5A
    max_current = 5.0  # Maximalstrom in Ampere
    
    # Map den Stromwert auf 0% bis 100%
    if current_in_amps < 0:
        return 0
    elif current_in_amps > max_current:
        return 100
    else:
        return (current_in_amps / max_current) * 100

# Hilfsfunktion zur Überprüfung, ob die aktuelle Zeit innerhalb eines Zeitplans liegt
def is_within_schedule(component):
    now = datetime.now().time()
    start_time = datetime.strptime(schedule[component]['start'], "%H:%M").time()
    end_time = datetime.strptime(schedule[component]['end'], "%H:%M").time()
    return start_time <= now <= end_time

# Steuerungsfunktionen
def control_device(component, action):
    pin = {"light": LIGHT_PIN, "pump": PUMP_PIN, "fan": FAN_PIN}.get(component)
    if pin:
        GPIO.output(pin, GPIO.HIGH if action == "on" else GPIO.LOW)

def check_soil_moisture(soil_value):
    water_level = get_water_level()
    if soil_value < 50 and water_level > 10:
        GPIO.output(PUMP_PIN, GPIO.LOW)
        logging.info("Pumpe eingeschaltet (Bodenfeuchtigkeit < 50% und Wassertand > 10%)")
        time.sleep(240)
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        logging.info("Pumpe nach 4 Minuten ausgeschaltet.")
    else:
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        logging.info("Pumpe ausgeschaltet (Bodenfeuchtigkeit >= 50% oder Wasserstand <= 10%)")

# API-Endpunkte
@app.route('/get_sensordata', methods=['GET'])
def get_sensordata():
    """Gibt die aktuellen Sensordaten zurück (direkt an die API gesendet)."""
    soil_moisture = get_soil_moisture()
    water_level = get_water_level()
    power_consumption = get_power_consumption()

    data = {
        "water_level": water_level,
        "soil_moisture": soil_moisture,
        "power_consumption": power_consumption
    }

    return jsonify(data)

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    """Setzt die Zeitpläne für die Geräte."""
    data = request.json
    logging.info(f"Empfangene Daten für Zeitplan: {data}")

    component = data.get('component')
    start_time = data.get('start')
    end_time = data.get('end')

    if not component or not start_time or not end_time:
        return jsonify({"error": "Fehlende erforderliche Parameter"}), 400

    if component in schedule:
        schedule[component]["start"] = start_time
        schedule[component]["end"] = end_time
        return jsonify({"message": f"Zeitplan für {component} aktualisiert."}), 200
    elif component == "fan_interval":
        schedule["fan_interval"] = data.get('interval', schedule["fan_interval"])
        schedule["fan_duration"] = data.get('duration', schedule["fan_duration"])
        return jsonify({"message": "Ventilator-Intervall und Dauer aktualisiert."}), 200
    else:
        return jsonify({"error": "Ungültige Komponente"}), 400

@app.route('/manual_control', methods=['POST'])
def manual_control_endpoint():
    """Manuelle Steuerung der Geräte (Licht, Pumpe, Ventilator)."""
    data = request.json
    logging.info(f"Empfangene Daten für manuelle Steuerung: {data}")

    component = data.get('component')
    action = data.get('action')

    if not component or not action:
        return jsonify({"error": "Fehlende erforderliche Parameter"}), 400

    if component not in ['light', 'pump', 'fan']:
        return jsonify({"error": "Ungültige Komponente"}), 400
    if action not in ['on', 'off']:
        return jsonify({"error": "Ungültige Aktion"}), 400

    manual_control[component] = (action == 'on')  # Speichert den manuellen Zustand
    control_device(component, action)
    return jsonify({"message": f"{component} wurde {action} geschaltet."}), 200

# Hintergrundschleifen
def sensor_data_loop():
    """Regelmäßige Aktualisierung der Sensorwerte und direkte Übertragung an die API alle 5 Minuten."""
    while True:
        soil_moisture = get_soil_moisture()
        water_level = get_water_level()
        power_consumption = get_power_consumption()

        data = {
            "water_level": water_level,
            "soil_moisture": soil_moisture,
            "power_consumption": power_consumption
        }

        # Sende die Sensordaten direkt an die API
        try:
            response = requests.post('http://127.0.0.1:5000/sensordata', json=data)  # Lokale API-URL
            if response.status_code != 200:
                logging.error(f"Fehler beim Senden der Sensordaten an die API: {response.status_code}")
        except Exception as e:
            logging.error(f"Fehler bei der Verbindung zur API: {e}")

        time.sleep(60)  # Jede Minute aktualisieren

def pump_control_loop():
    """Steuerung der Pumpe basierend auf Bodenfeuchtigkeit und Zeitplan."""
    while True:
        if is_within_schedule("pump") and not manual_control["pump"]:  # Nur im Zeitplan und wenn nicht manuell gesteuert
            soil_moisture = get_soil_moisture()
            water_level = get_water_level()
        
        if water_level > 10:
            check_soil_moisture(soil_moisture)  # Aufruf der Funktion zur Steuerung der Pumpe
        else:
            GPIO.output(PUMP_PIN, GPIO.LOW)
            logging.info("Pumpe ausgeschaltet")
        time.sleep(180)  # Überprüft alle 3 Minuten

def fan_control_loop():
    """Automatische Steuerung des Ventilators basierend auf Intervall und Dauer."""
    while True:
        if is_within_schedule("fan") and not manual_control["fan"]:  # Nur im Zeitplan und wenn nicht manuell gesteuert
            logging.info("Ventilator eingeschaltet (geplanter Intervall)")
            control_device("fan", "on")
            time.sleep(schedule["fan_duration"] * 60)  # Ventilator läuft für die eingestellte Dauer
            control_device("fan", "off")
            logging.info("Ventilator ausgeschaltet")
            time.sleep((schedule["fan_interval"] - schedule["fan_duration"]) * 60)  # Wartezeit bis zum nächsten Intervall
        else:
            time.sleep(60)  # Überprüfen jede Minute

def light_control_loop():
    """Automatische Steuerung des Lichts basierend auf dem Zeitplan."""
    while True:
        if is_within_schedule("light") and not manual_control["light"]:  # Nur im Zeitplan und wenn nicht manuell gesteuert
            logging.info("Licht eingeschaltet (geplanter Zeitrahmen)")
            control_device("light", "on")
        else:
            logging.info("Licht ausgeschaltet (außerhalb des Zeitrahmens)")
            control_device("light", "off")
        time.sleep(60)  # Überprüfen jede Minute

if __name__ == "__main__":
    # Hintergrund-Threads starten
    Thread(target=sensor_data_loop, daemon=True).start()
    Thread(target=pump_control_loop, daemon=True).start()
    Thread(target=fan_control_loop, daemon=True).start()
    Thread(target=light_control_loop, daemon=True).start()

    # Flask starten (auf der lokalen IP-Adresse)
    app.run(host="0.0.0.0", port=5000)
