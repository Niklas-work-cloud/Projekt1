import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

# Debugging-Ausgabe hinzufügen
print("Diagramm-Modul wird geladen.")  # Dies wird in der Konsole ausgegeben

def app():
    st.title("Diagramme")
    st.write("Hier befinden sich alle wichtigen Daten.")

# Testdaten für den Wasserstand (in Prozent) und Verlauf über den Tag
def generate_water_level_data():
    max_volume_liters = 500  # Maximaler Tankinhalt in Litern
    current_volume_liters = random.uniform(50, max_volume_liters)  # Zufälliger Wasserstand in Litern
    water_percentage = (current_volume_liters / max_volume_liters) * 100  # Prozentualer Wasserstand
    return current_volume_liters, water_percentage, max_volume_liters

def generate_water_level_over_day():
    hours = np.arange(0, 24)
    max_volume_liters = 500
    water_levels = [random.uniform(50, max_volume_liters) for _ in range(24)]  # Zufällige Wasserstände in Litern
    water_levels_percentage = [(level / max_volume_liters) * 100 for level in water_levels]
    return hours, water_levels_percentage

# Testdaten für den Stromverbrauch
def generate_power_consumption_data():
    current_consumption = random.uniform(0.5, 3.0)  # Aktueller Stromverbrauch in kWh
    return current_consumption

def generate_power_consumption_over_day():
    hours = np.arange(0, 24)  # Stunden des Tages
    power_consumption = [random.uniform(0.5, 3.0) for _ in range(24)]  # Zufälliger Stromverbrauch in kWh pro Stunde
    return hours, power_consumption

# Diagramm für den aktuellen Wasserstand als vertikales Balkendiagramm
def plot_current_water_level(parameter='percentage'):
    current_volume_liters, water_percentage, max_volume_liters = generate_water_level_data()

    fig, ax = plt.subplots(figsize=(6, 4))  # Etwas größere Diagrammgröße
    if parameter == 'liters':
        ax.bar(['Wasserstand'], [current_volume_liters], color='#1f77b4')
        ax.set_ylim(0, max_volume_liters)  # Y-Achse auf max. Volumen setzen
        ax.set_ylabel('Wasserstand (L)')
        ax.set_title(f"Wasserstand: {current_volume_liters:.1f} L / {max_volume_liters} L")
    else:
        ax.bar(['Wasserstand'], [water_percentage], color='#1f77b4')
        ax.set_ylim(0, 100)  # Y-Achse von 0 bis 100 Prozent
        ax.set_ylabel('Wasserstand in %')
        ax.set_title(f"Wasserstand: {water_percentage:.1f}%")
    
    return fig

# Diagramm für den Wasserstand über den Tag verteilt
def plot_water_level_over_day(parameter='percentage'):
    hours, water_levels_percentage = generate_water_level_over_day()
    water_levels_liters = [(level / 100) * 500 for level in water_levels_percentage]  # In Litern umrechnen

    fig, ax = plt.subplots(figsize=(6, 4))  # Etwas größere Diagrammgröße
    if parameter == 'liters':
        ax.plot(hours, water_levels_liters, color='#ff7f0e', marker='o', linestyle='-', linewidth=2, markersize=6)
        ax.set_ylabel('Wasserstand in Litern')
        ax.set_title('Wasserstand über den Tag verteilt (in Litern)')
    else:
        ax.plot(hours, water_levels_percentage, color='#ff7f0e', marker='o', linestyle='-', linewidth=2, markersize=6)
        ax.set_ylabel('Wasserstand in %')
        ax.set_title('Wasserstand über den Tag verteilt (in %)')

    ax.set_xlabel('Stunden des Tages')
    ax.grid(True)

    return fig

# Diagramm für den aktuellen Stromverbrauch als Balkendiagramm
def plot_current_power_consumption(parameter='kWh'):
    current_consumption = generate_power_consumption_data()

    fig, ax = plt.subplots(figsize=(6, 4))  # Etwas größere Diagrammgröße
    if parameter == 'kWh':
        ax.bar(['Aktueller Stromverbrauch'], [current_consumption], color='#2ca02c')  # Balkendiagramm für aktuellen Stromverbrauch
        ax.set_ylim(0, 5)  # Y-Achse von 0 bis 5 kWh
        ax.set_ylabel('Stromverbrauch (kWh)')
        ax.set_title(f"Aktueller Stromverbrauch: {current_consumption:.2f} kWh")
    else:
        ax.bar(['Aktueller Stromverbrauch'], [current_consumption * 1000], color='#2ca02c')  # Umgerechnet in Wh
        ax.set_ylim(0, 5000)  # Y-Achse von 0 bis 5000 Wh
        ax.set_ylabel('Stromverbrauch (Wh)')
        ax.set_title(f"Aktueller Stromverbrauch: {current_consumption * 1000:.0f} Wh")

    return fig

# Diagramm für den Stromverbrauch über den Tag verteilt (Balkendiagramm)
def plot_power_consumption_over_day(parameter='kWh'):
    hours, power_consumption = generate_power_consumption_over_day()
    power_consumption_wh = [consumption * 1000 for consumption in power_consumption]  # Umrechnung in Wh

    fig, ax = plt.subplots(figsize=(6, 4))  # Etwas größere Diagrammgröße
    if parameter == 'kWh':
        ax.bar(hours, power_consumption, color='#2ca02c')  # Balkendiagramm für Stromverbrauch in kWh
        ax.set_ylabel('Stromverbrauch (kWh)')
        ax.set_title('Stromverbrauch über den Tag verteilt (kWh)')
    else:
        ax.bar(hours, power_consumption_wh, color='#2ca02c')  # Balkendiagramm für Stromverbrauch in Wh
        ax.set_ylabel('Stromverbrauch (Wh)')
        ax.set_title('Stromverbrauch über den Tag verteilt (Wh)')

    ax.set_xlabel('Stunden des Tages')
    ax.grid(True)

    return fig

# Streamlit App
def app():
    st.title("📶 Datenüberwachung")

    # Sidebar Auswahl für die Diagramme
    st.sidebar.subheader('Diagramm-Parameter')

    # Auswahl der Diagramme und ihrer Parameter
    selected_data_water = st.sidebar.radio('Wählen Sie die Wasserstand-Ansicht', ('Aktueller Wasserstand', 'Wasserstand über den Tag'))
    selected_parameter_water = st.sidebar.selectbox('Wählen Sie die Einheit für Wasserstand', ('Prozent (%)', 'Liter (L)'))

    selected_data_power = st.sidebar.radio('Wählen Sie die Stromverbrauch-Ansicht', ('Aktueller Stromverbrauch', 'Stromverbrauch über den Tag'))
    selected_parameter_power = st.sidebar.selectbox('Wählen Sie die Einheit für Stromverbrauch', ('kWh', 'Wh'))

    # Diagramm 1: Aktueller Wasserstand
    if selected_data_water == 'Aktueller Wasserstand':
        st.subheader("📊 Aktueller Wasserstand")
        fig1 = plot_current_water_level(parameter='percentage' if selected_parameter_water == 'Prozent (%)' else 'liters')
        st.pyplot(fig1)  # Zeige das Diagramm

    # Diagramm 2: Wasserstand über den Tag
    if selected_data_water == 'Wasserstand über den Tag':
        st.subheader("📈 Wasserstand über den Tag verteilt")
        fig2 = plot_water_level_over_day(parameter='percentage' if selected_parameter_water == 'Prozent (%)' else 'liters')
        st.pyplot(fig2)  # Zeige das Diagramm

    # Diagramm 3: Aktueller Stromverbrauch
    if selected_data_power == 'Aktueller Stromverbrauch':
        st.subheader("🔌 Aktueller Stromverbrauch")
        fig3 = plot_current_power_consumption(parameter='kWh' if selected_parameter_power == 'kWh' else 'Wh')
        st.pyplot(fig3)  # Zeige das Diagramm

    # Diagramm 4: Stromverbrauch über den Tag
    if selected_data_power == 'Stromverbrauch über den Tag':
        st.subheader("🔌 Stromverbrauch über den Tag verteilt")
        fig4 = plot_power_consumption_over_day(parameter='kWh' if selected_parameter_power == 'kWh' else 'Wh')
        st.pyplot(fig4)  # Zeige das Diagramm

# Start der App
if __name__ == "__main__":
    app()