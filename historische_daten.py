import streamlit as st
import pandas as pd
import datetime

def app():
    st.title("📊 Historische Daten")
    st.write("In diesem Bereich können Sie die Verbrauchs- und Anbaudaten Ihrer Gardening Box einsehen.")

    # Initialisiere Beispiel-Daten (Simulation von Sensor-Daten)
    if "historical_data" not in st.session_state:
        st.session_state.historical_data = {
            "electricity": [
                {"date": "2024-11-01", "consumption": 3.5},
                {"date": "2024-11-02", "consumption": 4.0},
                {"date": "2024-11-03", "consumption": 3.8},
            ],
            "water": [
                {"date": "2024-11-01", "consumption": 50},
                {"date": "2024-11-02", "consumption": 45},
                {"date": "2024-11-03", "consumption": 48},
            ],
            "plants": [
                {"plant": "Lauchzwiebel", "planted": "2024-10-01", "harvested": "2024-12-15"},
            ],
        }

    # Verbrauchsdaten (Strom und Wasser) anzeigen
    st.subheader("Monatlicher Verbrauch")

    # Stromverbrauch
    st.write("### Stromverbrauch (kWh)")
    electricity_df = pd.DataFrame(st.session_state.historical_data["electricity"])
    if not electricity_df.empty:
        electricity_df["date"] = pd.to_datetime(electricity_df["date"])
        monthly_electricity = electricity_df.groupby(electricity_df["date"].dt.strftime('%Y-%m'))["consumption"].sum()
        st.line_chart(electricity_df.set_index("date")["consumption"])
        st.write(f"**Gesamter Stromverbrauch im Monat:** {monthly_electricity.iloc[-1]:.2f} kWh")
    else:
        st.write("Keine Daten zum Stromverbrauch verfügbar.")

    # Wasserverbrauch
    st.write("### Wasserverbrauch (Liter)")
    water_df = pd.DataFrame(st.session_state.historical_data["water"])
    if not water_df.empty:
        water_df["date"] = pd.to_datetime(water_df["date"])
        monthly_water = water_df.groupby(water_df["date"].dt.strftime('%Y-%m'))["consumption"].sum()
        st.line_chart(water_df.set_index("date")["consumption"])
        st.write(f"**Gesamter Wasserverbrauch im Monat:** {monthly_water.iloc[-1]:.2f} Liter")
    else:
        st.write("Keine Daten zum Wasserverbrauch verfügbar.")

    # Daten zurücksetzen
    st.write("### Daten zurücksetzen")
    if st.button("Alle historischen Daten löschen"):
        st.session_state.historical_data = {
            "electricity": [],
            "water": [],
            "plants": [],
        }
        st.warning("Alle Daten wurden gelöscht.")


