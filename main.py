import streamlit as st
from streamlit_option_menu import option_menu
import home
import diagramme
import zeitschaltplan
import wachstumsfortschritt
from dotenv import load_dotenv
import requests  # Zum Abrufen der Sensordaten von der Flask-API

# Umgebungsvariablen laden
load_dotenv()

# Flask-API-URL (stellen sicher, dass der Flask-Server läuft)
API_URL = "http://127.0.0.1:5000"  # Grund-URL zum Abrufen der Daten und Steuern der Geräte

# Funktion zum Abrufen der Sensordaten
def get_sensor_data():
    """Holt die Sensordaten von der Flask-API und gibt sie zurück."""
    try:
        response = requests.get(f"{API_URL}/get_sensordata")
        response.raise_for_status()  # Überprüfen, ob die Anfrage erfolgreich war
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Sensordaten: {e}")
        return None

# Funktion zum Senden von Steuerbefehlen (manuelles Ein-/Ausschalten der Geräte)
def control_device(component, action):
    """Sendet einen Steuerbefehl an die API, um das Gerät ein- oder auszuschalten."""
    try:
        response = requests.post(f"{API_URL}/control_device", json={"component": component, "action": action})
        response.raise_for_status()  # Überprüfen, ob die Anfrage erfolgreich war
        if response.status_code == 200:
            st.success(f"{component} wurde {action}!")
        else:
            st.error(f"Fehler beim Steuern des {component}.")
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Steuern des {component}: {e}")

# Streamlit-Seite konfigurieren
st.set_page_config(page_title="Grow Smart")

# MultiApp-Klasse für mehrere Apps
class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        with st.sidebar:
            st.sidebar.image("images/Grow_smart.png")
            st.markdown("---")

            app = option_menu(
                menu_title="🌱 Gardening Box",
                options=["Home", "Diagramme", "Zeitschaltplan", "Wachstumsfortschritt"],
                icons=["house-fill", "📊", "⏱️", "🌱"],
                menu_icon="🌱",
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "#f5f5f5"},
                    "icon": {"color": "#333", "font-size": "23px"},
                    "nav-link": {"color": "#333", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "#e5e5e5"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                },
            )

        # Sensordaten abrufen
        sensor_data = get_sensor_data()

        if sensor_data:
            # Zeige die aktuellen Sensordaten in der Sidebar oder auf der Startseite
            st.sidebar.subheader("Aktuelle Sensordaten")
            st.sidebar.write(f"Temperatur: {sensor_data.get('temperature')} °C")
            st.sidebar.write(f"Luftfeuchtigkeit: {sensor_data.get('humidity')} %")
            st.sidebar.write(f"Wasserstand: {sensor_data.get('water_percentage')} %")
        else:
            st.sidebar.write("Keine Sensordaten verfügbar.")

        # Aufruf der entsprechenden App-Funktion je nach Auswahl
        if app == "Home":
            home.app(sensor_data, control_device)  # Übergabe der Sensordaten und Steuerfunktion
        elif app == "Diagramme":
            diagramme.app()
        elif app == "Zeitschaltplan":
            zeitschaltplan.app()
        elif app == "Wachstumsfortschritt":
            wachstumsfortschritt.app()

# Hauptprogramm
if __name__ == "__main__":
    app = MultiApp()
    app.add_app("Home", home.app)
    app.add_app("Diagramme", diagramme.app)
    app.add_app("Zeitschaltplan", zeitschaltplan.app)
    app.add_app("Wachstumsfortschritt", wachstumsfortschritt.app)

    app.run()
