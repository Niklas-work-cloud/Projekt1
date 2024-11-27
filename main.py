# main.py
import streamlit as st
from streamlit_option_menu import option_menu
import home
import diagramme
import zeitschaltplan
import wachstumsfortschritt
import historische_daten
from dotenv import load_dotenv

# Umgebungsvariablen laden
load_dotenv()

# Streamlit-Seite konfigurieren
st.set_page_config(
    page_title="Pondering",
)

# MultiApp-Klasse für mehrere Apps
class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        with st.sidebar:
            st.sidebar.image("images/Grow_smart.png")
            st.markdown("---")

            app = option_menu(
                menu_title="🌱 Gardening Box",
                options=["Home", "Diagramme", "Zeitschaltplan", "Wachstumsfortschritt", "Historische Daten"],
                icons=["house-fill", "📊", "⏱️", "🌱", "clock"],
                menu_icon="🌱",
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "#f5f5f5"},
                    "icon": {"color": "#333", "font-size": "23px"},
                    "nav-link": {
                        "color": "#333",
                        "font-size": "20px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#e5e5e5",
                    },
                    "nav-link-selected": {"background-color": "#02ab21"},
                },
            )

        # Aufruf der entsprechenden App-Funktion je nach Auswahl
        if app == "Home":
            home.app()
        elif app == "Diagramme":
            diagramme.app()
        elif app == "Zeitschaltplan":
            zeitschaltplan.app()
        elif app == "Wachstumsfortschritt":
            wachstumsfortschritt.app()
        elif app == "Historische Daten":
            historische_daten.app()

# Hauptprogramm
if __name__ == "__main__":
    app = MultiApp()

    app.add_app("Home", home.app)
    app.add_app("Diagramme", diagramme.app)
    app.add_app("Zeitschaltplan", zeitschaltplan.app)
    app.add_app("Wachstumsfortschritt", wachstumsfortschritt.app)
    app.add_app("Historische Daten", historische_daten.app)
    
    app.run()
