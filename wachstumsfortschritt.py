import streamlit as st
from PIL import Image, ImageDraw
import datetime

# Wachstumsdaten der Lauchzwiebeln
def get_growth_data(week):
    # Wachstum in cm pro Woche
    growth_per_week = [0, 1, 3, 5, 8, 12, 15, 20, 25, 30, 35, 40]  # Wachstum in cm
    if week < len(growth_per_week):
        return growth_per_week[week - 1]  # Gibt die Höhe der Pflanze für die Woche zurück
    else:
        return growth_per_week[-1]  # Maximale Höhe nach Woche 12 (30-40 cm)

# Erstelle das Bild der Pflanze basierend auf der Höhe
def create_growth_image(plant_height_cm):
    img_size = (150, 300)  # Bildgröße
    img = Image.new('RGB', img_size, color=(255, 255, 255))  # Weißer Hintergrund
    draw = ImageDraw.Draw(img)
    
    # Umwandlung der Höhe von cm in Pixel
    plant_height_pixels = int(plant_height_cm * 7)  # Skalierung von cm zu Pixeln
    
    # Pflanze zeichnen (grünes Rechteck)
    plant_position = (50, img_size[1] - plant_height_pixels)  # Position der Pflanze
    draw.rectangle([plant_position, (100, img_size[1])], fill="green")
    
    return img

# Erstelle das Bild der fertigen Pflanze (maximale Größe)
def create_finished_image():
    plant_height_cm = 40  # Maximale Höhe der Pflanze
    return create_growth_image(plant_height_cm)

# Haupt-App-Funktion
def app():
    st.title("🌱 Wachstumsfortschritt der Lauchzwiebeln")

    # Anzeige des Level in der Sidebar
    if "level" not in st.session_state:
        st.session_state.level = 0  # Startlevel ist 0
    
    # Anzeige des Level-Fortschritts in der Sidebar
    st.sidebar.header(f"Level: {st.session_state.level}")

    # Historische Daten initialisieren, falls nicht vorhanden
    if "history" not in st.session_state:
        st.session_state.history = []

    # Überprüfen, ob das Pflanzdatum im session_state gespeichert ist, andernfalls setzen
    if "plant_date" not in st.session_state:
        st.session_state.plant_date = datetime.date.today()
        st.session_state.weeks_passed = 0  # Zu Beginn sind 0 Wochen vergangen

    # Benutzer gibt das Pflanzdatum ein (das Startdatum der Pflanze)
    plant_date = st.date_input("Wann hast du die Lauchzwiebeln gepflanzt?", st.session_state.plant_date)

    # Berechne, wie viele Wochen seit dem Pflanzdatum vergangen sind
    today = datetime.date.today()
    weeks_passed = (today - plant_date).days // 7  # Berechne die vergangenen Wochen

    # Wenn weniger als eine Woche vergangen ist, setze die Woche auf 1
    if weeks_passed < 1:
        weeks_passed = 1  # Damit es mindestens eine Woche gibt

    # Wenn das Pflanzdatum geändert wird, setzen wir den Fortschritt zurück
    if plant_date != st.session_state.plant_date:
        st.session_state.plant_date = plant_date  # Speichern des neuen Pflanzdatums
        st.session_state.weeks_passed = 0  # Setze die Woche zurück

    st.session_state.weeks_passed = weeks_passed  # Aktualisiere die Woche im session_state

    # Berechne die Höhe der Pflanze basierend auf der Woche
    plant_height_cm = get_growth_data(weeks_passed)

    # Erstelle die Bilder für den Wachstumsfortschritt und die fertige Pflanze
    growth_image = create_growth_image(plant_height_cm)
    finished_image = create_finished_image()

    # Zeige die Bilder nebeneinander an
    col1, col2 = st.columns(2)

    with col1:
        st.image(growth_image, caption=f"Wachstumsfortschritt der Lauchzwiebel: Woche {weeks_passed}", width=150)
        st.write(f"Die Pflanze ist aktuell {plant_height_cm} cm hoch.")
    
    with col2:
        st.image(finished_image, caption="Fertige Lauchzwiebel (maximale Größe: 40 cm)", width=150)
        st.write("Die Lauchzwiebel ist in Woche 12 vollständig gewachsen.")

    # Zeige aktuelle Woche und Fortschritt an
    st.subheader(f"Aktuelle Woche: {weeks_passed}")
    st.write(f"Die Lauchzwiebel wächst in Woche {weeks_passed} und ist derzeit {plant_height_cm} cm groß.")

    # Anzeige, wenn 12 Wochen erreicht sind
    if weeks_passed >= 12:
        st.warning("⚠️ Die Lauchzwiebel ist jetzt bereit zur Ernte! 🌾")

    # Ernten-Button
    if st.button("Ernten! 🌾"):
        # Belohnung
        st.success("🎉 Herzlichen Glückwunsch! Du hast erfolgreich geerntet! 🎉")
        st.balloons()  # Ballons als visuelle Belohnung
        st.write("Du erhältst 10 Punkte für deine erfolgreiche Ernte! Weiter so! 🚀")
        
        # Historische Daten aktualisieren: wenn Ernte stattfindet
        harvest_info = {
            "plant_date": st.session_state.plant_date,
            "harvest_date": today,
            "plant_height_cm": plant_height_cm,
            "status": "Geerntet"
        }
        st.session_state.history.append(harvest_info)  # Speichern der Ernte in den historischen Daten
        
        # Level erhöhen
        st.session_state.level += 1  # Hier wird der Level um 1 erhöht (kann angepasst werden)

    # Anzeige der historischen Anbaudaten
    if st.session_state.history:
        st.subheader("📜 Historische Anbaudaten")
        for record in st.session_state.history:
            st.write(f"🌱 Pflanzdatum: {record['plant_date']} | Erntedatum: {record['harvest_date']} | Status: {record['status']}")

# Start der App
if __name__ == "__main__":
    app()
