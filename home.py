import streamlit as st
import requests
import time

# Funktion zum Abrufen der Sensordaten von der API
def get_sensor_data():
    """Holt die Sensordaten von der Flask-API und gibt sie zurück."""
    API_URL = "http://127.0.0.1:5000"  # API-URL anpassen, falls nötig
    try:
        response = requests.get(f"{API_URL}/get_sensordata")
        response.raise_for_status()  # Überprüfen, ob die Anfrage erfolgreich war
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Sensordaten: {e}")
        return None

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

# Funktion zur Steuerung der Komponente und Senden von API-Anfragen
def manual_control(component, label, control_device):
    """Steuert die Komponente manuell (ein- oder ausschalten)."""
    if st.session_state.control_mode.get(component, "automatisch") == "manuell":
        # Button für Einschalten
        if st.button(f"{label} Einschalten", key=f"{component}_on"):
            # Status direkt im session_state aktualisieren
            st.session_state.component_status[component] = True
            # Sende das Signal an die API, um die Komponente einzuschalten
            control_device(component, "on")
        
        # Button für Ausschalten
        if st.button(f"{label} Ausschalten", key=f"{component}_off"):
            # Status direkt im session_state aktualisieren
            st.session_state.component_status[component] = False
            # Sende das Signal an die API, um die Komponente auszuschalten
            control_device(component, "off")
    else:
        st.info(f"{label} wird im **automatischen Modus** gesteuert.")

# Haupt-App
def app(sensor_data, control_device):
    # Überprüfe, ob die erforderlichen Schlüssel existieren, andernfalls initialisiere sie
    if "component_status" not in st.session_state:
        st.session_state.component_status = {"light": False, "pump": False, "fan": False}

    if "control_mode" not in st.session_state:
        st.session_state.control_mode = {"light": "automatisch", "pump": "automatisch", "fan": "automatisch"}

    st.title("🏠 Home")
    st.write("Willkommen im Home-Bereich der Gardening Box! 🏡")
    st.write("**Hinweis:** Umschalten zwischen Automatisch und Manuell für jede Komponente.")

    # Steuerung der Komponenten
    for component, label in [("light", "💡 Licht"), ("pump", "💧 Pumpe"), ("fan", "☢ Ventilator")]:
        st.subheader(label)
        col1, col2, col3 = st.columns([1, 1.5, 2])

        # Spalte 1: Label und Status
        with col1:
            st.markdown("**Status:**", unsafe_allow_html=True)
            st.markdown(display_status(component, st.session_state.component_status[component]), unsafe_allow_html=True)

        # Spalte 2: Modus umschalten
        with col2:
            control_mode_switch(component, label)

        # Spalte 3: Steuerung basierend auf Modus
        with col3:
            manual_control(component, label, control_device)

        # Trennlinie für Übersichtlichkeit
        st.markdown("---")

# Hauptprogramm
def main():
    # Initialisieren der Steuerfunktion
    def manual_control(component, action):
        """Steuert ein Gerät basierend auf den API-Befehlen."""
        try:
            # API-Endpunkt für manuelle Steuerung verwenden
            response = requests.post(f"http://127.0.0.1:5000/manual_control", json={"component": component, "action": action})
            response.raise_for_status()
            if response.status_code == 200:
                # Erfolgsnachricht mit dem neuen Format: {component} ist {action}
                actions_translation = {"on": "eingeschaltet", "off": "ausgeschaltet"}
                st.success(f"{component} hab {actions_translation[action]}!")
            else:
                st.error(f"Fehler beim Steuern des {component}. Antwort: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Fehler beim Steuern des {component}: {e}")

    # Abrufen der Sensordaten und App aufrufen
    while True:
        sensor_data = get_sensor_data()
        if sensor_data:
            app(sensor_data, manual_control)
        else:
            st.error("Es konnte keine Verbindung zur API hergestellt werden.")
        
        time.sleep(30)  # Wartezeit vor dem nächsten Abruf der Sensordaten (jetzt 30 Sekunden)
        st.experimental_rerun()  # Wiederhole das Abrufen und die Anzeige der Daten

# Hauptprogramm ausführen
if __name__ == "__main__":
    main()