import streamlit as st
import requests

# API-Konfigurationsvariablen
API_BASE_URL = "http://127.0.0.1:5000"
API_CONTROL_ENDPOINT = "/control_device"
API_SENSOR_ENDPOINT = "/sensor_data"

# Funktion zur Anzeige des Status
def display_status(component, active):
    """Erstellt den HTML-Code für die Statusanzeige."""
    if st.session_state.control_mode.get(component, "automatisch") == "automatisch":
        return '<span style="color:white;background-color:grey;padding:5px 10px;border-radius:5px;">Automatisch</span>'
    elif active:
        return '<span style="color:white;background-color:green;padding:5px 10px;border-radius:5px;">Eingeschaltet</span>'
    else:
        return '<span style="color:white;background-color:red;padding:5px 10px;border-radius:5px;">Ausgeschaltet</span>'

# Funktion zur Steuerung des Modus
def control_mode_switch(component, label):
    """Steuert den Modus für die Komponente (manuell oder automatisch)."""
    mode = st.radio(
        f"Modus für {label}",
        options=["manuell", "automatisch"],
        key=f"{component}_mode",
        index=0 if st.session_state.control_mode.get(component, "automatisch") == "manuell" else 1,
    )
    st.session_state.control_mode[component] = mode

# Funktion zur Steuerung der Komponente
def manual_control(component, label):
    """Steuert die Komponente manuell (ein- oder ausschalten)."""
    if st.session_state.control_mode.get(component, "automatisch") == "manuell":
        # Button für Einschalten
        if st.button(f"{label} Einschalten", key=f"{component}_on"):
            try:
                response = control_device(component, "on")
                if response.status_code == 200:
                    st.session_state.component_status[component] = True
                    st.success(f"{label} wurde eingeschaltet.")
                else:
                    st.error(f"Fehler: {response.text}")
            except Exception as e:
                st.error(f"Fehler beim Steuern des {component}: {e}")
        
        # Button für Ausschalten
        if st.button(f"{label} Ausschalten", key=f"{component}_off"):
            try:
                response = control_device(component, "off")
                if response.status_code == 200:
                    st.session_state.component_status[component] = False
                    st.success(f"{label} wurde ausgeschaltet.")
                else:
                    st.error(f"Fehler: {response.text}")
            except Exception as e:
                st.error(f"Fehler beim Steuern des {component}: {e}")
    else:
        st.info(f"{label} wird im **automatischen Modus** gesteuert.")

# Funktion zum Abrufen von Sensordaten
def fetch_sensor_data():
    """Ruft Sensordaten von der API ab."""
    try:
        response = requests.get(API_BASE_URL + API_SENSOR_ENDPOINT)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Fehler beim Abrufen der Sensordaten: {response.text}")
            return None
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Sensordaten: {e}")
        return None

# Funktion zur Steuerung der Geräte
def control_device(component, action):
    """Sendet Steuerungsbefehle an die API."""
    try:
        response = requests.post(API_BASE_URL + API_CONTROL_ENDPOINT, json={"component": component, "action": action})
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"API-Fehler: {e}")
        raise

# Funktion zur Alarmierung bei niedrigem Wasserstand
def check_water_level(water_percentage):
    """Prüft den Wasserstand und gibt eine Warnung aus, wenn der Wasserstand unter 20% fällt."""
    if water_percentage < 20:
        st.warning("⚠️ **Alarm: Wasserstand unter 20%!** Bitte Wasser nachfüllen.")
    else:
        st.success("💧 Der Wasserstand ist ausreichend.")

# Haupt-App
def app():
    # Initialisierung
    if "component_status" not in st.session_state:
        st.session_state.component_status = {"light": False, "pump": False, "fan": False}

    if "control_mode" not in st.session_state:
        st.session_state.control_mode = {"light": "automatisch", "pump": "automatisch", "fan": "automatisch"}

    # Titel und Info
    st.title("🏠 Home")
    st.write("Willkommen im Home-Bereich der Gardening Box! Umschalten zwischen Automatisch und Manuell für jede Komponente.")

    # Sensordaten
    sensor_data = fetch_sensor_data()
    if sensor_data:
        # Wasserstand
        st.subheader(f"Wasserstand: {sensor_data['current_volume_liters']} L / {sensor_data['max_volume_liters']} L")
        st.progress(int(sensor_data["water_percentage"]))
        check_water_level(sensor_data["water_percentage"])

        # Temperatur und Luftfeuchtigkeit
        st.subheader(f"🌡️ Temperatur: {sensor_data['temperature']} °C")
        st.subheader(f"💧 Luftfeuchtigkeit: {sensor_data['humidity']} %")
    else:
        st.error("Sensordaten konnten nicht abgerufen werden.")

    # Komponenten-Steuerung
    for component, label in [("light", "💡 Licht"), ("pump", "💧 Pumpe"), ("fan", "☢ Ventilator")]:
        st.subheader(label)
        col1, col2, col3 = st.columns([1, 1.5, 2])

        # Spalte 1: Status
        with col1:
            st.markdown("**Status:**", unsafe_allow_html=True)
            st.markdown(display_status(component, st.session_state.component_status[component]), unsafe_allow_html=True)

        # Spalte 2: Modus
        with col2:
            control_mode_switch(component, label)

        # Spalte 3: Steuerung
        with col3:
            manual_control(component, label)

        st.markdown("---")  # Trennlinie

# App starten
if __name__ == "__main__":
    app()
