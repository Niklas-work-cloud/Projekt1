import streamlit as st
import pandas as pd
import requests
import datetime

# API-Endpunkte (angepasst an deine API-URL)
API_URL_ELECTRICITY = "http://127.0.0.1:5000/get_historical_data?data_type=electricity"
API_URL_WATER = "http://127.0.0.1:5000/get_historical_data?data_type=water"

# Funktion zum Abrufen der Daten von der API
def get_data_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Falls der HTTP-Statuscode nicht 200 ist, wird eine Ausnahme ausgelöst
        return response.json()  # Rückgabe der Antwort als JSON
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
        return []  # Rückgabe einer leeren Liste bei Fehler

def app():
    st.title("📊 Historische Daten")
    st.write("In diesem Bereich können Sie die Verbrauchsdaten Ihrer Gardening Box einsehen.")

    # Verbrauchsdaten (Strom und Wasser) anzeigen
    st.subheader("Täglicher Verbrauch")

    # Stromverbrauch
    st.write("### Stromverbrauch (kWh)")
    electricity_data = get_data_from_api(API_URL_ELECTRICITY)
    if electricity_data:
        electricity_df = pd.DataFrame(electricity_data)
        electricity_df["date"] = pd.to_datetime(electricity_df["date"])  # Datetime konvertieren
        electricity_df.set_index("date", inplace=True)
        
        # Gruppiere nach Tag und summiere den Verbrauch
        daily_electricity = electricity_df.resample('D')["consumption"].sum()
        
        # Zeige den täglichen Verbrauch als Liniendiagramm
        st.line_chart(daily_electricity)
        
        # Gesamten Stromverbrauch des letzten Tages anzeigen
        st.write(f"**Gesamter Stromverbrauch am letzten Tag:** {daily_electricity.iloc[-1]:.2f} kWh")
    else:
        st.write("Keine Daten zum Stromverbrauch verfügbar.")

    # Wasserverbrauch
    st.write("### Wasserverbrauch (Liter)")
    water_data = get_data_from_api(API_URL_WATER)
    if water_data:
        water_df = pd.DataFrame(water_data)
        water_df["date"] = pd.to_datetime(water_df["date"])  # Datetime konvertieren
        water_df.set_index("date", inplace=True)
        
        # Gruppiere nach Tag und summiere den Verbrauch
        daily_water = water_df.resample('D')["consumption"].sum()
        
        # Zeige den täglichen Verbrauch als Liniendiagramm
        st.line_chart(daily_water)
        
        # Gesamten Wasserverbrauch des letzten Tages anzeigen
        st.write(f"**Gesamter Wasserverbrauch am letzten Tag:** {daily_water.iloc[-1]:.2f} Liter")
    else:
        st.write("Keine Daten zum Wasserverbrauch verfügbar.")

# Start der App
if __name__ == "__main__":
    app()
