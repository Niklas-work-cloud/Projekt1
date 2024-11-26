import streamlit as st
from datetime import time

# Debugging-Ausgabe hinzufügen
print("Zeitschaltplan-Modul wird geladen.")  # Dies wird in der Konsole ausgegeben

def app():
    st.title("⏱️ Zeitschaltplan Steuerung")
    st.write("Dies ist der Zeitschaltplan.")

    # Weitere Debugging-Ausgabe
    print("Zeitschaltplan App-Funktion wird aufgerufen.")  # Wird in der Konsole ausgegeben, wenn die Funktion aufgerufen wird

    # Initialisierung der Zeitsteuerung im Session State
    if "time_schedule" not in st.session_state:
        st.session_state.time_schedule = {
            "light": {"start": time(6, 0), "end": time(18, 0)},  # Licht von 06:00 bis 18:00
            "pump": {"start": time(22, 0), "end": time(6, 0)},  # Pumpe von 22:00 bis 06:00 deaktiviert
            "fan": {"start": time(0, 0), "end": time(0, 0)},  # Ventilator, hier Initialwerte setzen
            "fan_interval": 15,  # Standard Intervall (15 Minuten)
            "fan_duration": 5  # Standard Dauer (5 Minuten)
        }

    # Funktion zur Eingabe von Zeit für Licht und Pumpe
    def time_input(label, key, default_start, default_end):
        start_time = st.time_input(f"Startzeit {label}", default_start, key=f"{key}_start")
        end_time = st.time_input(f"Endzeit {label}", default_end, key=f"{key}_end")
        return start_time, end_time

    # Funktion zur Eingabe der Intervall- und Dauer-Einstellungen für den Ventilator
    def fan_schedule_input():
        # Intervall in 15-Minuten-Schritten (15, 30, 45, 60, ...)
        interval_options = [15, 30, 45, 60, 75, 90, 105, 120]
        interval = st.selectbox("Ventilator Intervall (Minuten)", interval_options, index=interval_options.index(st.session_state.time_schedule["fan_interval"]))
        
        # Dauer als Dropdown (zwischen 1 und 10 Minuten)
        duration = st.selectbox("Ventilator Dauer (Minuten)", options=range(1, 11), index=st.session_state.time_schedule["fan_duration"] - 1)
        
        return interval, duration

    # Licht Steuerung
    st.markdown("<h3 style='color:green;'>Licht Steuerung</h3>", unsafe_allow_html=True)
    light_start, light_end = time_input("Licht", "light", st.session_state.time_schedule["light"]["start"], st.session_state.time_schedule["light"]["end"])
    st.session_state.time_schedule["light"]["start"] = light_start
    st.session_state.time_schedule["light"]["end"] = light_end

    # Pumpe Steuerung
    st.markdown("<h3 style='color:green;'>Pumpe Steuerung</h3>", unsafe_allow_html=True)
    pump_start, pump_end = time_input("Pumpe", "pump", st.session_state.time_schedule["pump"]["start"], st.session_state.time_schedule["pump"]["end"])
    st.session_state.time_schedule["pump"]["start"] = pump_start
    st.session_state.time_schedule["pump"]["end"] = pump_end

    # Ventilator Steuerung
    st.markdown("<h3 style='color:green;'>Ventilator Steuerung</h3>", unsafe_allow_html=True)
    fan_interval, fan_duration = fan_schedule_input()
    
    st.session_state.time_schedule["fan_interval"] = fan_interval
    st.session_state.time_schedule["fan_duration"] = fan_duration

    # Zeitschaltpläne anzeigen
    st.write("### Aktuelle Zeitschaltpläne:")
    st.write(f"Licht: {st.session_state.time_schedule['light']['start']} - {st.session_state.time_schedule['light']['end']}")
    st.write(f"Pumpe: {st.session_state.time_schedule['pump']['start']} - {st.session_state.time_schedule['pump']['end']}")
    st.write(f"Ventilator: Alle {fan_interval} Minuten für {fan_duration} Minuten")

# Start der App
if __name__ == "__main__":
    app()
