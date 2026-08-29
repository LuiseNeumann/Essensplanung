print("donnee")

import json
import random

print("Starte Skript...")  # Testausgabe

# Datei laden
with open("rezepte.json", encoding="utf-8") as f:
    datenbank = json.load(f)

# Testausgabe
print(type(datenbank))  # <class 'list'>

# Auswahl
zufaellige_gerichte = random.sample(datenbank, 5)

# Ergebnis anzeigen
for gericht in zufaellige_gerichte:
    print(gericht["name"])
#
input("Drücke Enter zum Beenden...")

