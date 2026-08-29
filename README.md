# Essensplanung

Web-App zur wöchentlichen Essensplanung mit saisonalen Rezeptvorschlägen, Einkaufsliste und Wochenspeicher.

## Features

- Zufällige/zufallsgefilterte Rezeptauswahl für eine planbare Anzahl an Tagen
- Filter nach maximaler Kochdauer und Saisonalität (monatsbasiert)
- Saisonkalender für Obst, Gemüse und Salat
- Automatische Einkaufsliste, gruppiert nach Kategorien
- Woche speichern und später einsehen

## Voraussetzungen

- Python 3.8 oder neuer
- Flask

## Installation

```bash
pip install flask
```

## Starten

```bash
python app.py
```

Anschließend http://127.0.0.1:5000 im Browser öffnen.

## Projektstruktur

- `app.py` – Flask-Backend mit allen Routen
- `rezepte.json` – Rezeptdatenbank
- `saisonkalender_*.json` – Saisonkalender für Obst, Gemüse, Salat
- `templates/` – HTML-Templates (Jinja2)
- `static/` – JavaScript, CSS, Bilder, Service-Worker

## Daten anpassen

Rezepte werden in `rezepte.json` gepflegt. Jedes Rezept braucht die Felder
`id`, `name`, `kochdauer_minuten`, `schwierigkeit`, `zutaten` und `beschreibung`.
Jede Zutat benötigt `name`, `menge` und `kategorie`.
