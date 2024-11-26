import streamlit as st
import random

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
        if st.button(f"{label} Einschalten", key=f"{component}_on"):
            st.session_state.component_status[component] = True
        if st.button(f"{label} Ausschalten", key=f"{component}_off"):
            st.session_state.component_status[component] = False
    else:
        st.info(f"{label} wird im **automatischen Modus** gesteuert.")

# Funktion zur Alarmierung bei niedrigem Wasserstand
def check_water_level(water_percentage):
    """Prüft den Wasserstand und gibt eine Warnung aus, wenn der Wasserstand unter 20% fällt."""
    if water_percentage < 20:
        st.warning("⚠️ **Alarm: Wasserstand unter 20%!** Bitte Wasser nachfüllen.")
    else:
        st.success("💧 Der Wasserstand ist ausreichend.")

# Funktionen zum Erzeugen von Demo-Daten für Wasserstand, Temperatur und Luftfeuchtigkeit
def generate_water_level_data():
    max_volume_liters = 500
    current_volume_liters = random.uniform(50, max_volume_liters)
    water_percentage = (current_volume_liters / max_volume_liters) * 100
    return current_volume_liters, water_percentage, max_volume_liters

def generate_temperature():
    return random.uniform(18, 30)  # Temperatur zwischen 18 und 30 Grad Celsius

def generate_humidity():
    return random.uniform(40, 80)  # Luftfeuchtigkeit zwischen 40% und 80%

# Haupt-App
def app():
    # Überprüfe, ob die erforderlichen Schlüssel existieren, andernfalls initialisiere sie
    if "component_status" not in st.session_state:
        st.session_state.component_status = {"light": False, "pump": False, "fan": False}

    if "control_mode" not in st.session_state:
        st.session_state.control_mode = {"light": "automatisch", "pump": "automatisch", "fan": "automatisch"}

    st.title("🏠Home")
    st.write("Willkommen im Home-Bereich der Gardening Box!")

    st.write("**Hinweis:** Umschalten zwischen Automatisch und Manuell für jede Komponente.")

    # Generiere und zeige Wasserstand
    current_volume_liters, water_percentage, max_volume_liters = generate_water_level_data()
    st.subheader(f"Wasserstand: {current_volume_liters:.1f} L / {max_volume_liters} L")
    st.progress(int(water_percentage))  # Zeige den Wasserstand als Fortschrittsbalken
    check_water_level(water_percentage)  # Alarm bei niedrigem Wasserstand

    # Generiere und zeige Temperatur und Luftfeuchtigkeit
    temperature = generate_temperature()
    humidity = generate_humidity()
    st.subheader(f"🌡️ Temperatur: {temperature:.2f} °C")
    st.subheader(f"💧 Luftfeuchtigkeit: {humidity:.2f} %")

    # Steuerung der Komponenten
    for component, label in [("light", "💡 Licht"), ("pump", "💧 Pumpe"), ("fan", "☢ Ventilator")]:
        # Sicherstellen, dass der Status der Komponente im Session State vorhanden ist
        if component not in st.session_state.component_status:
            st.session_state.component_status[component] = False
        if component not in st.session_state.control_mode:
            st.session_state.control_mode[component] = "automatisch"

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
            manual_control(component, label)

        # Trennlinie für Übersichtlichkeit
        st.markdown("---")

# Start der App
if __name__ == "__main__":
    app()
