import streamlit as st
import matplotlib.pyplot as plt
import requests

# URL der API
API_URL = "http://127.0.0.1:5000"

# Funktion zum Abrufen der Sensordaten von der API
def get_sensor_data():
    try:
        response = requests.get(f"{API_URL}/get_sensordata")
        response.raise_for_status()
        return response.json()  # Wir nehmen an, die Antwort ist im JSON-Format
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Sensordaten: {e}")
        return None

# Funktion zur Anzeige von Temperatur und Feuchtigkeit
def display_temperature_humidity(sensor_data):
    """Zeigt die Temperatur und Luftfeuchtigkeit an."""
    st.subheader(f"🌡️ Temperatur: {sensor_data['temperature']} °C")
    st.subheader(f"💧 Luftfeuchtigkeit: {sensor_data['humidity']} %")

# Diagramm für den aktuellen Stromverbrauch
def plot_current_power_consumption(sensor_data):
    """Erstellt das Diagramm für den aktuellen Stromverbrauch"""
    current_consumption = sensor_data['power_consumption']

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Aktueller Stromverbrauch'], [current_consumption], color='#2ca02c')
    ax.set_ylim(0, 5)  # Optional: Anpassen der Y-Achse
    ax.set_ylabel('Stromverbrauch (kWh)')
    ax.set_title(f"Aktueller Stromverbrauch: {current_consumption:.2f} kWh")
    return fig

# Diagramm für den Wasserstand (in Prozent)
def plot_water_level(sensor_data):
    """Erstellt das Diagramm für den Wasserstand"""
    water_percentage = sensor_data["water_percentage"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Wasserstand'], [water_percentage], color='#1f77b4')
    ax.set_ylim(0, 100)
    ax.set_ylabel('Wasserstand in %')
    ax.set_title(f"Wasserstand: {water_percentage:.1f}%")
    return fig

# Streamlit App
def app():
    st.title("📶 Datenüberwachung")

    # Button, um die Daten zu aktualisieren
    if st.button("Daten aktualisieren"):
        # Abrufen der Sensordaten
        sensor_data = get_sensor_data()

        if sensor_data:
            # Container für die Diagramme
            # Diagramm für den Wasserstand
            water_level_container = st.empty()
            water_level_container.subheader("📊 Aktueller Wasserstand")
            fig1 = plot_water_level(sensor_data)
            water_level_container.pyplot(fig1)

            # Diagramm für den Stromverbrauch
            power_consumption_container = st.empty()
            power_consumption_container.subheader("🔌 Aktueller Stromverbrauch")
            fig2 = plot_current_power_consumption(sensor_data)
            power_consumption_container.pyplot(fig2)

            # Diagramm für Temperatur und Luftfeuchtigkeit
            temperature_humidity_container = st.empty()
            display_temperature_humidity(sensor_data)
        else:
            st.error("Sensordaten konnten nicht abgerufen werden.")

if __name__ == "__main__":
    app()
