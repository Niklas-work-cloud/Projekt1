from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, time
import random
import logging
import json

app = Flask(__name__)
CORS(app)  # Cross-Origin Resource Sharing aktivieren

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dummy GPIO-Steuerung für Windows
class GPIO:
    BCM = 0
    OUT = 0
    HIGH = 1
    LOW = 0

    @staticmethod
    def setmode(mode):
        logging.info(f"GPIO setmode to {mode}")

    @staticmethod
    def setup(pin, mode):
        logging.info(f"GPIO setup: Pin {pin} in mode {mode}")

    @staticmethod
    def output(pin, state):
        logging.info(f"GPIO output: Pin {pin} set to {'HIGH' if state == GPIO.HIGH else 'LOW'}")

    @staticmethod
    def cleanup():
        logging.info("GPIO cleanup")

# GPIO-Pin-Konfiguration
LIGHT_PIN = 17
PUMP_PIN = 27
FAN_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_PIN, GPIO.OUT)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)

# Zeitplan-Datenstruktur
time_schedule = {
    "light": {"start": time(6, 0), "end": time(18, 0)},
    "pump": {"start": time(22, 0), "end": time(6, 0)},
    "fan": {"start": time(6, 0), "end": time(18, 0), "interval": 30, "duration": 5}
}

# Hilfsfunktionen zur Konvertierung von time zu String und zurück
def time_to_str(t):
    return t.strftime('%H:%M') if isinstance(t, time) else t

def str_to_time(t_str):
    return datetime.strptime(t_str, '%H:%M').time()

# Simulierte Sensordaten
def read_sensors():
    try:
        current_volume_liters = random.uniform(50, 500)
        max_volume_liters = 500
        water_percentage = (current_volume_liters / max_volume_liters) * 100

        temperature = random.uniform(18, 30)
        humidity = random.uniform(40, 80)
        soil_moisture = random.uniform(10, 90)

        power_consumption = random.uniform(100, 300)

        pump_status = "on" if soil_moisture < 30 and water_percentage > 20 else "off"
        GPIO.output(PUMP_PIN, GPIO.HIGH if pump_status == "on" else GPIO.LOW)

        light_status = "on" if 6 <= datetime.now().hour < 18 else "off"
        GPIO.output(LIGHT_PIN, GPIO.HIGH if light_status == "on" else GPIO.LOW)

        minute = datetime.now().minute
        fan_status = "on" if minute % time_schedule["fan"]["interval"] < time_schedule["fan"]["duration"] else "off"
        GPIO.output(FAN_PIN, GPIO.HIGH if fan_status == "on" else GPIO.LOW)

        return {
            "current_volume_liters": round(current_volume_liters, 2),
            "max_volume_liters": max_volume_liters,
            "water_percentage": round(water_percentage, 2),
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "soil_moisture": round(soil_moisture, 2),
            "power_consumption": round(power_consumption, 2),
            "pump_status": pump_status,
            "light_status": light_status,
            "fan_status": fan_status
        }
    except Exception as e:
        logging.error(f"Fehler beim Lesen der Sensoren: {e}")
        raise

# Endpunkte
@app.route('/get_sensordata', methods=['GET'])
def get_sensordata():
    try:
        data = read_sensors()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Fehler beim Abrufen der Sensordaten", "details": str(e)}), 500

@app.route('/control_device', methods=['POST'])
def control_device():
    try:
        data = request.json
        component = data.get('component')
        action = data.get('action')

        if component not in ['light', 'pump', 'fan']:
            return jsonify({"error": "Ungültige Komponente"}), 400
        if action not in ['on', 'off']:
            return jsonify({"error": "Ungültige Aktion"}), 400

        if component == "light":
            GPIO.output(LIGHT_PIN, GPIO.HIGH if action == "on" else GPIO.LOW)
        elif component == "pump":
            GPIO.output(PUMP_PIN, GPIO.HIGH if action == "on" else GPIO.LOW)
        elif component == "fan":
            GPIO.output(FAN_PIN, GPIO.HIGH if action == "on" else GPIO.LOW)

        logging.info(f"{component} wurde {action} geschaltet.")
        return jsonify({"message": f"{component} wurde {action} geschaltet."}), 200
    except Exception as e:
        logging.error(f"Fehler bei der Gerätesteuerung: {e}")
        return jsonify({"error": "Fehler bei der Gerätesteuerung", "details": str(e)}), 500

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    try:
        data = request.json
        component = data.get('component')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if component not in ['light', 'pump', 'fan']:
            return jsonify({"error": "Ungültige Komponente"}), 400
        if not start_time or not end_time:
            return jsonify({"error": "Start- und Endzeit müssen angegeben werden"}), 400

        start_time = str_to_time(start_time)
        end_time = str_to_time(end_time)

        # Update Zeitplan
        time_schedule[component]["start"] = start_time
        time_schedule[component]["end"] = end_time

        if component == "fan":
            interval = data.get('interval', time_schedule["fan"].get('interval', 30))
            duration = data.get('duration', time_schedule["fan"].get('duration', 5))
            time_schedule[component]["interval"] = interval
            time_schedule[component]["duration"] = duration

        logging.info(f"Zeitplan für {component} aktualisiert: {time_schedule[component]}")
        return jsonify({"message": f"{component} Zeitplan wurde erfolgreich aktualisiert."}), 200
    except Exception as e:
        logging.error(f"Fehler beim Aktualisieren des Zeitplans: {e}")
        return jsonify({"error": "Fehler beim Aktualisieren des Zeitplans", "details": str(e)}), 500

@app.route('/get_schedule', methods=['GET'])
def get_schedule():
    try:
        # Serialisiere die Zeitdaten als Strings
        serialized_schedule = {
            component: {
                "start": time_to_str(schedule["start"]),
                "end": time_to_str(schedule["end"]),
                "interval": schedule.get("interval"),
                "duration": schedule.get("duration")
            }
            for component, schedule in time_schedule.items()
        }
        return jsonify(serialized_schedule)
    except Exception as e:
        return jsonify({"error": "Fehler beim Abrufen des Zeitplans", "details": str(e)}), 500

@app.teardown_appcontext
def cleanup_gpio(exception=None):
    GPIO.cleanup()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
