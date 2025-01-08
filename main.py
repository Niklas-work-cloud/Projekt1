import streamlit as st
from streamlit_option_menu import option_menu
import home
import diagramme
import zeitschaltplan
import wachstumsfortschritt
from dotenv import load_dotenv
import requests

# Umgebungsvariablen laden
load_dotenv()

# Flask-API-URL (stellen sicher, dass der Flask-Server läuft)
API_URL = "http://127.0.0.1:5000"

# Funktion zum Abrufen der Sensordaten
def get_sensor_data():
    """Holt die Sensordaten von der Flask-API und gibt sie zurück."""
    try:
        response = requests.get(f"{API_URL}/get_sensordata")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Sensordaten: {e}")
        return None

# Funktion zum Senden von Steuerbefehlen (manuelles Ein-/Ausschalten der Geräte)
def manual_control(component, action):
    """Sendet einen Steuerbefehl an die API, um das Gerät ein- oder auszuschalten."""
    try:
        response = requests.post(f"{API_URL}/manual_control", json={"component": component, "action": action})
        response.raise_for_status()
        if response.status_code == 200:
            st.success(f"{component} is {action}!")
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
        
        st.sidebar.markdown("## 🌿 Lauchzwiebel 🪴")
        
        # Sensordaten abrufen
        sensor_data = get_sensor_data()

        # Aufruf der entsprechenden App-Funktion je nach Auswahl
        if app == "Home":
            if sensor_data:  # Überprüfen, ob Sensordaten erfolgreich abgerufen wurden
                home.app(sensor_data, manual_control)  # Übergebe sowohl Sensordaten als auch Steuerfunktion
            else:
                st.error("Es konnten keine Sensordaten abgerufen werden.")
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
