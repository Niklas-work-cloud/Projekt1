import random  # Temporär für simulierte Werte

def read_sensors():
    # Simulierte Sensorwerte
    temperature = random.uniform(18, 30)
    humidity = random.uniform(40, 80)
    soil_moisture = random.uniform(10, 90)
    return {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "soil_moisture": round(soil_moisture, 2),
    }

print(read_sensors())
