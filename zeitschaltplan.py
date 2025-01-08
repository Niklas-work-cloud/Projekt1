import streamlit as st
from datetime import time
import requests  # Für API-Anfragen

# API-Konfigurationsvariablen
API_BASE_URL = "http://127.0.0.1:5000"  # IP-Adresse und Port des Raspberry Pi
API_ENDPOINT_SCHEDULE = "/set_schedule"
API_GET_SCHEDULE = "/get_schedule"

def send_schedule_to_api(component, schedule_data):
    """
    Sendet Zeitpläne für ein bestimmtes Gerät an die API.
    :param component: Name der Komponente (z. B. "light", "pump", "fan")
    :param schedule_data: Zeitplan-Daten (Dictionary mit Zeitplan-Informationen)
    """
    data = {"component": component, **schedule_data}
    try:
        response = requests.post(API_BASE_URL + API_ENDPOINT_SCHEDULE, json=data)
        if response.status_code == 200:
            st.success(f"Zeitplan für {component} erfolgreich aktualisiert.")
        else:
            st.error(f"Fehler bei der Aktualisierung des Zeitplans: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"API-Fehler: {e}")

def fetch_current_schedule():
    """
    Ruft den aktuellen Zeitplan von der API ab.
    :return: Dictionary mit den Zeitplänen oder Standardwerte.
    """
    try:
        response = requests.get(API_BASE_URL + API_GET_SCHEDULE)
        if response.status_code == 200:
            schedule_data = response.json()
            # Sicherstellen, dass alle Zeiten als datetime.time Objekte vorliegen
            for component in schedule_data:
                # Umwandlung von String-Zeitformaten (falls vorhanden) in time-Objekte
                if isinstance(schedule_data[component]["start"], str):
                    start_hour, start_minute = map(int, schedule_data[component]["start"].split(":"))
                    schedule_data[component]["start"] = time(start_hour, start_minute)
                if isinstance(schedule_data[component]["end"], str):
                    end_hour, end_minute = map(int, schedule_data[component]["end"].split(":"))
                    schedule_data[component]["end"] = time(end_hour, end_minute)
            return schedule_data
        else:
            st.warning("Konnte Zeitpläne nicht abrufen. Standardwerte werden verwendet.")
            return get_default_schedule()
    except requests.exceptions.RequestException as e:
        st.error(f"API-Fehler: {e}")
        return get_default_schedule()

def get_default_schedule():
    """
    Liefert Standardwerte für die Zeitpläne.
    :return: Dictionary mit Standardzeitplänen.
    """
    return {
        "light": {"start": time(6, 0), "end": time(18, 0)},
        "pump": {"start": time(22, 0), "end": time(6, 0)},
        "fan": {"start": time(6, 0), "end": time(18, 0), "interval": 30, "duration": 5},
    }

def app():
    st.title("⏱️ Zeitschaltplan Steuerung")
    st.write("Definieren Sie Zeitpläne für die Steuerung von Licht, Pumpe und Ventilator.")

    # Zeitplan laden
    if "time_schedule" not in st.session_state:
        st.session_state.time_schedule = fetch_current_schedule()

    # Funktion zur Eingabe von Zeitplänen
    def time_input(label, component_key, default_start, default_end):
        start_time = st.time_input(f"Startzeit {label}", value=default_start, key=f"{component_key}_start")
        end_time = st.time_input(f"Endzeit {label}", value=default_end, key=f"{component_key}_end")
        return start_time, end_time

    # Komponenten-Steuerung
    components = ["light", "pump", "fan"]
    for component in components:
        st.markdown(f"<h3 style='color:green;'>{component.capitalize()} Steuerung</h3>", unsafe_allow_html=True)

        # Zeitplan-Eingabe
        start, end = time_input(
            component.capitalize(),
            component,
            st.session_state.time_schedule[component]["start"],
            st.session_state.time_schedule[component]["end"],
        )

        # Ventilator-Spezialfälle
        if component == "fan":
            interval = st.selectbox(
                "Intervall (Minuten)",
                options=[15, 30, 45, 60, 120],
                index=[15, 30, 45, 60, 120].index(st.session_state.time_schedule[component]["interval"]),
                key=f"{component}_interval",
            )
            duration = st.selectbox(
                "Dauer (Minuten)",
                options=range(5, 61, 5),
                index=(st.session_state.time_schedule[component]["duration"] // 5) - 1,
                key=f"{component}_duration",
            )

            # Wenn Änderungen vorgenommen wurden, diese an die API senden
            if (
                start != st.session_state.time_schedule[component]["start"]
                or end != st.session_state.time_schedule[component]["end"]
                or interval != st.session_state.time_schedule[component]["interval"]
                or duration != st.session_state.time_schedule[component]["duration"]
            ):
                st.session_state.time_schedule[component] = {
                    "start": start,
                    "end": end,
                    "interval": interval,
                    "duration": duration,
                }
                send_schedule_to_api(
                    component,
                    {
                        "start_time": start.strftime("%H:%M"),
                        "end_time": end.strftime("%H:%M"),
                        "interval": interval,
                        "duration": duration,
                    },
                )
        else:
            # Für Licht und Pumpe
            if start != st.session_state.time_schedule[component]["start"] or end != st.session_state.time_schedule[component]["end"]:
                st.session_state.time_schedule[component] = {"start": start, "end": end}
                send_schedule_to_api(
                    component,
                    {"start_time": start.strftime("%H:%M"), "end_time": end.strftime("%H:%M")},
                )

    # Übersicht der Zeitpläne
    st.write("### Aktuelle Zeitpläne:")
    for component, schedule in st.session_state.time_schedule.items():
        if component == "fan":
            st.write(
                f"- **{component.capitalize()}**: {schedule['start']} - {schedule['end']}, "
                f"Intervall: {schedule['interval']} Minuten, Dauer: {schedule['duration']} Minuten"
            )
        else:
            st.write(f"- **{component.capitalize()}**: {schedule['start']} - {schedule['end']}")

# Start der App
if __name__ == "__main__":
    app()
