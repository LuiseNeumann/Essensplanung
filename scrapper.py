import requests
from bs4 import BeautifulSoup
import json

url = "https://www.regional-saisonal.de/saisonkalender-salat"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Monate definieren
monate = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

# Tabelle finden
table = soup.find("table")
saisonkalender = {}

for row in table.find_all("tr")[1:]:  # Kopfzeile überspringen
    cols = row.find_all("td")
    name = cols[0].text.strip()  # Gemüse-Namen aus erster Spalte holen
    saison_monate = []

    for i, col in enumerate(cols[1:]):  # Monats-Spalten durchgehen
        img = col.find("img")  # Bild-Tag suchen
        if img and img.get("alt") == "ja":  # Falls ein Bild mit "ja" vorhanden ist
            saison_monate.append(monate[i])

    saisonkalender[name] = saison_monate  # Nur Monate speichern, in denen das Gemüse Saison hat

# Speichern als JSON
with open("saisonkalender_salat.json", "w", encoding="utf-8") as f:
    json.dump(saisonkalender, f, ensure_ascii=False, indent=4)

print("Saisonkalender erfolgreich gespeichert!")
