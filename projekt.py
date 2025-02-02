import spidev
import time
import RPi.GPIO as GPIO
from datetime import datetime, time as datetime_time
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread

app = Flask(__name__)
CORS(app)

#app.run(host="0.0.0.0", port=5000)

GPIO.setmode(GPIO.BCM)

PUMP_PIN = 26
LIGHT_PIN = 16
FAN_PIN = 13

GPIO.setup(PUMP_PIN,GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(LIGHT_PIN, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 1350000

schedules = {
    "light": {"start": datetime_time(6,0),"end":datetime_time(18,0)},
    "pump": {"start":datetime_time(6,0),"end":datetime_time(18,0)},
    "fan": {"start":datetime_time(10,0),"end":datetime_time(18,0), "interval": 30, "duration": 5},
}

control_mode = {
    "light": "automatisch",
    "pump": "automatisch",
    "fan": "automatisch"
}

component_status = {
    "light": False,
    "pump": False,
    "fan": False
}
    

#control_mode = {
 #   "light": "automatisch",
  #  "pump": "automatisch",
   # "fan": "automatisch"
#}

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def get_soil_moisture():
    soil_value = read_adc(0)
    print(f"Bodenfeuchtigkeit: {soil_value}")
    if soil_value > 650:
        return 0
    elif soil_value < 310:
        return 100
    else:
        return ((650 - soil_value) / (650 - 310)) *100

def get_water_level():
    water_value = read_adc(1)
    print(f"Wasserstand: {water_value}")
    if water_value >= 670: 
        return 100
    elif water_value >= 660:
        return 90
    elif water_value >= 655:
        return 80
    elif water_value >= 650:
        return 75
    elif water_value >= 640:
        return 70
    elif water_value>= 625:
        return 60
    elif water_value >= 600:
        return 50
    elif water_value >= 575:
        return 40
    elif water_value >=550:
        return 30
    elif water_value >= 520:
        return 25
    elif water_value >= 495:
        return 20
    elif water_value >=460:
        return 10
    elif water_value < 0:
        return 0
    else:
        return (water_value / 600) *100
    
def get_power_consumption():
    power_value = read_adc(2)
    print(f"Stromverbrauch: {power_value}")
    voltage = (power_value / 1023.0) * 5
    current_in_amps = ((voltage - 2.5) / 0.066)*-1
    print(f"Stromverbrauch in Amper: {current_in_amps:.2f}A")
    max_current = 5.0
    verbrauch = voltage * current_in_amps
    print(f"{verbrauch:.2f}W")
    
    return verbrauch

def fetch_current_schedule():
    try:
        response = requests.get("http://172.20.10.2:5000/get_schedule")
        if response.status_code == 200:
            schedule_data = response.json()
            return schedule_data
        else:
            return {}
    except requests.exceptions.RequestException as e:
        return {}
    

def fetch_manual():
    try:
        response = requests.get("http://172.20.10.2:5000/get_update_status")
        if response.status_code == 200:
            mode_data = response.json()
            return mode_data
        else:
            return {}
    except requests.exceptions.RequestException as e:
        return {}
    
def control_component(component, action):
    global component_status
    if action == "on":
        component_status[component] = True
        
    elif action == "off":
        component_status[component] = False
    else:
        print("not")

def is_within_schedule(component):

 #   sched = fetch_schedule_from_api()
    
    now = datetime.now().time()
    sched = fetch_current_schedule()
    
    if component in sched:
        start_time_str = sched[component]["start"]
        end_time_str = sched[component]["end"]
        print(now)
        #print(f"zeit:{sched}")
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(start_time_str, "%H:%M").time()
        if start_time <= now <= end_time:
            return True
        else:
            return False
    else:
        return False
        
            
        #return start_time <= now <= end_time
    #else:
        #return False

def control_device(component, action):
    pin = {"light": LIGHT_PIN, "pump": PUMP_PIN, "fan": FAN_PIN}.get(component)
    if action == "on":
        GPIO.output(pin, GPIO.LOW)
    else:
        GPIO.output(pin, GPIO.HIGH)

def check_soil_moisture(soil_value):
    water_level = get_water_level()
    if soil_value < 42 and water_level > 10:
        GPIO.output(PUMP_PIN, GPIO.LOW)
        time.sleep(270)
        GPIO.output(PUMP_PIN, GPIO.HIGH)
    else:
        GPIO.output(PUMP_PIN, GPIO.HIGH)

@app.route("/get_sensordata", methods=["GET"])
def get_sensordata():
    soil_moisture = get_soil_moisture()
    water_level = get_water_level()
    power_consumption = get_power_consumption()
    
    data = {
        "water_level": water_level,
        "soil_moisture": soil_moisture,
        "power_consumption": power_consumption
        }
    
    return jsonify(data)

@app.route("/get_manual_control", methods=["GET"])
def get_manual_control():
    return jsonify({
        "status": component_status,
        "modes": control_mode
    })

@app.route("/get_update_status", methods=["GET"])
def get_update_status():
    return jsonify({
        "status": component_status,
        "modes": control_mode
    })

@app.route("/set_manual_control", methods = ["GET"])
def set_manual_control():
    data = request.json
    component = data.get("component")
    action = data.get("action")
    mode = mode.get("mode")
    
    if component and action:
        control_component[component] = mode
        if mode:
            control_mode[component] = mode
        
        return jsonify({
            "message": f"{component} wurde {action} und der Modus wurde auf {mode} gesetzt.",
            "status": component_status,
            "modes": control_mode
        })
    else:
        return jsonify({"error"}), 400

@app.route("/set_update_status", methods=["POST"])
def set_update_status():
    data = request.json
    global component_status, control_mode
    
    component_status = data.get("status", component_status)
    control_mode = data.get("modes", control_mode)
    
    return jsonify({"success"
    })
        

@app.route("/get_action", methods=["GET"])
def get_action():
    schedule_data = {
        component: {
            "status": comp["status"]if isinstance(comp["status"],str) else print("ja")
        }
        for component, comp in compi.items()
    }
    return jsonify(schedule_data)

@app.route("/get_schedule", methods=["GET"])
def get_schedule():
    schedule_data = {
        component: {
            "start": schedule["start"]if isinstance(schedule["start"],str) else schedule["start"].strftime("%H:%M"),
            "end": schedule["end"]if isinstance(schedule["end"],str) else schedule["end"].strftime("%H:%M"),
            "interval": schedule.get("interval", None),
            "duration": schedule.get("duration", None),
        }
        for component, schedule in schedules.items()
    }
    return jsonify(schedule_data)


@app.route("/set_schedule", methods=["POST"])
def set_schedule():
    data = request.json
    
    component = data.get("component")
    start_time = data.get("start")
    end_time = data.get("end")
    interval_time = data.get("interval")
    duration_time = data.get("duration")
    
    if not component or not start_time or not end_time:
        return jsonify({"error": "Fehlende erforderliche Parameter"}),400#hhhhhieiier
    
    if component in schedules:
        schedules[component]["start"] = start_time
        schedules[component]["end"] = end_time
        schedules[component]["interval"] = interval_time
        schedules[component]["duration"] = duration_time
        
        #print(f"Zeitplan: {schedules}")
        
        return jsonify({"message": f"Zeitplan für {component} aktualisiert."}), 200
    else:
        return jsonify({"error": "Ungültige Komponente"}), 400

    
@app.route("/set_action", methods=["POST"])
def set_action():
    try:
        data = request.get_json()
        print(data)
        component = data.get("component")
        action = data.get("action")
        
        if component not in components:
            return jsonify ({"error": "Fehlende erforderliche Parameter"}), 400
        
        if components[component]["mode"] != "manuell":
            return jsonify ({"sstatus": "error", "message": f"{component} ist nicht im manuellen Modus"}), 400
        
        if action not in ["on", "off"]:
            return jsonfiy ({"error"})
        
        components[component]["status"] = action == "on"
        
        return jsonify({"status": "success", "component": component, "action": action}), 200
    except Exception as e:
        return jsonify({"error"})

def sensor_data_loop():
    while True:
        soil_moisture = get_soil_moisture()
        water_level = get_water_level()
        power_consumption = get_power_consumption()
        
        data = {
            "water_level": water_level,
            "soil_moisture": soil_moisture,
            "power_consumption": power_consumption
        }
        
        try:
            response = requests.post("http://172.20.10.2:5000/sensordata", json=data)
            if response.status_code !=200:
                print("ja")
        except Exception as ex:
            print(ex)
        time.sleep(200)

def pump_control_loop():
    while True:
        now = datetime.now().strftime("%H:&M")
        sched = fetch_current_schedule()
        soil_moisture = get_soil_moisture()
        water_level = get_water_level()
        manual = fetch_manual()
        if "status" in manual:
            #print(manual)
            pump_status = manual["status"]["pump"]
            if "pump" in sched:
                print(f"Pump:{pump_status}")
            #print(manual)
                pump_start = sched["pump"]["start"]
                pump_end = sched["pump"]["end"]
                if pump_start <= now <= pump_end:
                    if pump_status == False:
                        if water_level > 10:
                            check_soil_moisture(soil_moisture)
                        else:
                            GPIO.output(PUMP_PIN, GPIO.HIGH)
        time.sleep(3)

def fan_control_loop():
    while True:
        now = datetime.now().strftime("%H:&M")
        sched = fetch_current_schedule()
        manual = fetch_manual()
        if "status" in manual:
            #print(manual)
            fan_status = manual["status"]["fan"]
            if "fan" in sched:
                print(f"fan:{fan_status}")
                fan_start = sched["fan"]["start"]
                fan_end = sched["fan"]["end"]
                fan_intervall = sched["fan"]["interval"]
                fan_duration = sched["fan"]["duration"]
                if fan_start <= now <= fan_end:
                    if fan_status == False:
                        print((fan_intervall)*60)
                        time.sleep((fan_intervall)*60)
                        GPIO.output(FAN_PIN, GPIO.LOW)
                        print((fan_duration)*60)
                        time.sleep((fan_duration)*60)
                        GPIO.output(FAN_PIN, GPIO.HIGH)
                else:
                    GPIO.output(FAN_PIN, GPIO.HIGH)
                
        time.sleep(5)

def light_control_loop():
    while True:
        now = datetime.now().strftime("%H:&M")
        sched = fetch_current_schedule()
        manual = fetch_manual()
        #print(sched)
        if "status" in manual:
            #print(manual)
            light_status = manual["status"]["light"]
        if "light" in sched:
            print(f"light:{light_status}")
            light_start = sched["light"]["start"]
            light_end = sched["light"]["end"]
            if light_start <= now <= light_end:
                if light_status == False:
                    GPIO.output(LIGHT_PIN, GPIO.LOW)
            else:
                GPIO.output(LIGHT_PIN, GPIO.HIGH)

        time.sleep(5)
        
def pump_manual_loop():
    while True:
        now = datetime.now().strftime("%H:&M")
        manual = fetch_manual()
        water_level = get_water_level()
        if water_level > 10:
            if "status" in manual:
                    #print(manual)
                pump_status = manual["status"]["pump"]
                if pump_status == True:
                    GPIO.output(PUMP_PIN, GPIO.LOW)             
                elif pump_status == None:
                    GPIO.output(PUMP_PIN, GPIO.HIGH)
                else:
                    print("automatisch")
        else:
            GPIO.output(PUMP_PIN, GPIO.HIGH)
            
                    
        time.sleep(5)

def fan_manual_loop():
    while True:
        now = datetime.now().strftime("%H:&M")
        manual = fetch_manual()
        #print(manual)
        if "status" in manual:
            #print(manual)
            fan_status = manual["status"]["fan"]
            if fan_status == True:
                GPIO.output(FAN_PIN, GPIO.LOW)
            elif fan_status == None:
                GPIO.output(FAN_PIN, GPIO.HIGH)
            else:
                print("automatisch")
        time.sleep(5)

def light_manual_loop():
    while True:
        now = datetime.now().strftime("%H:&M")
        manual = fetch_manual()
        #print(manual)
        if "status" in manual:
            #print(manual)
            light_status = manual["status"]["light"]
            if light_status == True:
                GPIO.output(LIGHT_PIN, GPIO.LOW)
            elif light_status == None:
                GPIO.output(LIGHT_PIN, GPIO.HIGH)
            else:
                print("automatisch")
        time.sleep(5)
                
#app.run(host="172.20.10.2", port=5000)
if __name__ == "__main__":
    Thread(target=sensor_data_loop, daemon=True).start()
    Thread(target=pump_manual_loop, daemon=True).start()
    Thread(target=pump_control_loop, daemon=True).start()
    Thread(target=fan_control_loop, daemon=True).start()
    Thread(target=light_control_loop, daemon=True).start()
    Thread(target=fan_manual_loop, daemon=True).start()
    Thread(target=light_manual_loop, daemon=True).start()
    
app.run(host="172.20.10.2", port=5000)


#@app.route("/set_mode", methods=["POST"])
def set_mode():
    try:
        data = request.json
        component = data.get("component")
        mode = data.get("mode")
        
        if component not in components:
            return jsonify({"error"}),404
        if mode not in ["manuell", "automatisch"]:
            return jsonify({"error"}),400
        
        components[component] = mode
        
        if mode == "automatisch":
            components[component]["status"] = False
        return jsonify({"status": "success", "component": component, "mode": mode}), 200
    except Exception as e:
        return jsonify({"error"}), 500