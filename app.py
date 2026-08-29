#from flask import Flask, jsonify, request
from flask import Flask, render_template, jsonify, request,  redirect, url_for, session
import random
import json
from collections import defaultdict
import re
import datetime
import logging
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

app = Flask(__name__)
app.secret_key = 'geheim123'  #

#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

with open("rezepte.json", "r", encoding="utf-8") as f:
    rezepte = json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/zufall")
def zufall():
    return jsonify(random.sample(rezepte, 5))

@app.route("/gericht-tauschen")
def gericht_tauschen():
    return jsonify(random.choice(rezepte))

#if __name__ == "__main__":
 #   app.run(debug=True)
@app.route("/Einkaufsliste", methods=["POST"])
def einkaufsliste():
    daten = request.get_json()
    gerichte = daten["gerichte"]

    kategorien = defaultdict(dict)
    #kategorien = {
    #    "Obst": [],
     #   "Gemüse": [],
      #  "Tiefkühlprodukte": [],
       # "Kühlprodukte": [],
    #    "Gebäck": [],
     #   "Konserven": [],
      #  "Anderes": []
    #}

    for gericht in gerichte:
        for zutat in gericht.get("zutaten", []):
            name = zutat.get("name")
            menge = zutat.get("menge")
            kategorie = zutat.get("kategorie", "Anderes")

            # Versuche Zahl und Einheit zu trennen
            match = re.match(r"(\d+)\s*(\w*)", menge)
            if match:
                menge_wert = int(match.group(1))
                einheit = match.group(2)
            else:
                # Fallback wenn Format nicht erkannt wird
                menge_wert = 1
                einheit = menge

            key = f"{name} {einheit}".strip()

            # Summieren
            if key in kategorien[kategorie]:
                kategorien[kategorie][key] += menge_wert
            else:
                kategorien[kategorie][key] = menge_wert

    # Formatierung für die Ausgabe
    result = {}
    for kat, zutaten in kategorien.items():
        result[kat] = [f"{menge} {name}" for name, menge in zutaten.items()]


    return jsonify(result)

@app.route("/speichere-woche", methods=["POST"])
def speichere_woche():
    daten = request.get_json()
    session["geplante_woche"] = daten["gerichte"]
    return jsonify({"status": "gespeichert"})

@app.route("/meine-woche", methods=["GET", "POST"])
def meine_woche():
    plan = session.get("geplante_woche")

    if plan:
        wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        gerichte_map = {wochentage[i]: plan[i] for i in range(len(plan))}

        kategorien = {
            "Obst": {}, "Gemüse": {}, "Tiefkühlprodukte": {},
            "Kühlprodukte": {}, "Konserven": {}, "Gebäck": {}, "Anderes": {}
        }

        for gericht in plan:
            for zutat in gericht.get("zutaten", []):
                name = zutat.get("name")
                menge = zutat.get("menge", "1")
                kat = zutat.get("kategorie", "Anderes") or "Anderes"

                try:
                    teile = menge.split()
                    menge_wert = float(teile[0])
                    einheit = " ".join(teile[1:]) if len(teile) > 1 else ""
                except:
                    menge_wert = 1
                    einheit = menge

                schlüssel = (name, einheit)
                zutaten_dict = kategorien.setdefault(kat, {})
                if schlüssel in zutaten_dict:
                    zutaten_dict[schlüssel] += menge_wert
                else:
                    zutaten_dict[schlüssel] = menge_wert 

        einkaufsliste = {}
        for kat, zutaten in kategorien.items():
            einkaufsliste[kat] = [
                f"{menge:.0f} {einheit} {name}" if einheit else f"{menge:.0f} {name}"
                for (name, einheit), menge in zutaten.items()
            ]

        return render_template("meine_woche.html", plan=gerichte_map, einkaufsliste=einkaufsliste)

    return render_template("meine_woche.html", plan=None)


@app.route("/meine-woche/loeschen", methods=["POST"])
def loesche_woche():
    session.pop("geplante_woche", None)
    return redirect(url_for("meine_woche"))

@app.route("/rezepte")
def rezepte_anzeigen():
    with open('rezepte.json', 'r', encoding='utf-8') as f:
        rezepte = json.load(f)
    return render_template("rezepte.html", rezepte=rezepte)

#@app.route("/saisonkalender")
#def saisonkalender():
 #   return render_template("saisonkalender.html")

def lade_json(dateipfad):
    with open(dateipfad, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/saisonkalender")
def saisonkalender():
    obst = lade_json("saisonkalender_obst.json")
    gemuese = lade_json("saisonkalender_gemuese.json")
    salat = lade_json("saisonkalender_salat.json")
    return render_template("saisonkalender.html", obst=obst, gemuese=gemuese, salat=salat)


def lade_saisonkalender():
    """Lädt alle Saisonkalender-Daten"""
    saisonkalender = {}
    try:
        saisonkalender.update(lade_json("saisonkalender_obst.json"))
        saisonkalender.update(lade_json("saisonkalender_gemuese.json"))
        saisonkalender.update(lade_json("saisonkalender_salat.json"))
    except FileNotFoundError:
        print("Saisonkalender-Dateien nicht gefunden")
    return saisonkalender

def berechne_saisonalitaets_score(rezept, monat=None):
    """Berechnet Saisonalitäts-Score für ein Rezept"""
    if monat is None:
        monat = datetime.datetime.now().strftime("%B")
        # Deutsche Monatsnamen
        monat_mapping = {
            "January": "Januar", "February": "Februar", "March": "März",
            "April": "April", "May": "Mai", "June": "Juni",
            "July": "Juli", "August": "August", "September": "September",
            "October": "Oktober", "November": "November", "December": "Dezember"
        }
        monat = monat_mapping.get(monat, monat)
    
    saisonkalender = lade_saisonkalender()
    
    gemuese_zutaten = [z for z in rezept.get("zutaten", []) 
                       if z.get("kategorie") in ["Gemüse", "Obst"]]
    
    if not gemuese_zutaten:
        return {"score": 0, "treffer": 0,"gesamt": 0, "details": ["Keine saisonalen Zutaten"], "bewertung":"neutral" }
    
    saison_treffer = 0
    gesamt_zutaten = len(gemuese_zutaten)
    details = []
    
    for zutat in gemuese_zutaten:
        name = zutat.get("name", "").lower()
        # Versuche verschiedene Schreibweisen
        gefunden = False
        for saisonname, monate in saisonkalender.items():
            if name in saisonname.lower() or saisonname.lower() in name:
                if monat in monate:
                    saison_treffer += 1
                    details.append(f"✓ {zutat['name']} (Saison)")
                else:
                    details.append(f"✗ {zutat['name']} (keine Saison)")
                gefunden = True
                break
        if not gefunden:
            details.append(f"? {zutat['name']} (unbekannt)")
    
    score_prozent = (saison_treffer / gesamt_zutaten * 100) if gesamt_zutaten > 0 else 0
    
    return {
        "score": score_prozent,
        "treffer": saison_treffer,
        "gesamt": gesamt_zutaten,
        "details": details,
        "bewertung": "gut" if score_prozent >= 70 else "mittel" if score_prozent >= 40 else "schlecht"
    }

@app.route("/rezepte-gefiltert", methods=["POST"])
def rezepte_gefiltert():
    """Endpoint für gefilterte Rezepte"""
    try:
        daten = request.get_json()
        filter_saisonalitaet = daten.get("saisonalitaet", False)
        max_kochdauer_str = daten.get("max_kochdauer", None)
        monat = daten.get("monat", None)
        anzahl = daten.get("anzahl", 5)

        max_kochdauer = None
        if max_kochdauer_str and max_kochdauer_str.strip():
            try:
                max_kochdauer = int(max_kochdauer_str)
            except ValueError:
                print(f"Ungültige Kochdauer: {max_kochdauer_str}")
                max_kochdauer = None
        
        print(f"Filter - Saisonal: {filter_saisonalitaet}, Kochdauer: {max_kochdauer}, Monat: {monat}")
        
        gefilterte_rezepte = []
        
        for rezept in rezepte:
            # Kochdauer-Filter
            original_kochdauer = rezept.get("kochdauer_minuten")
            print(f"Rezept '{rezept.get('name', 'unbekannt')}': kochdauer_minuten = {original_kochdauer}")
            
            if max_kochdauer is not None:
                if "kochdauer_minuten" in rezept:
                    rezept_kochdauer = rezept["kochdauer_minuten"]
                else:
                    print(f"WARNUNG: Rezept '{rezept.get('name')}' hat kein 'kochdauer_minuten' Feld!")
                    rezept_kochdauer = None  # oder einen anderen Standardwert
                
                if rezept_kochdauer is not None and rezept_kochdauer > max_kochdauer:
                    continue
        
                    
            # Saisonalitäts-Filter
            saison_info = berechne_saisonalitaets_score(rezept, monat)
            if filter_saisonalitaet and saison_info["score"] < 40:  # Mindestens 40% saisonal
                continue
                
            if "kochdauer_minuten" not in rezept or rezept["kochdauer_minuten"] is None:
                print(f"Setze Standard-Kochdauer für '{rezept.get('name')}'")
                rezept["kochdauer_minuten"] = 30  # Oder einen anderen sinnvollen Standardwert
                    
            rezept["saisonalitaets_info"] = saison_info
            gefilterte_rezepte.append(rezept)
        
        print(f"Gefilterte Rezepte: {len(gefilterte_rezepte)}")
        
        # Wenn zu wenige Rezepte, erweitere die Kriterien
        if len(gefilterte_rezepte) < anzahl:
            print("Erweitere Kriterien...")
            for rezept in rezepte:
                if rezept in gefilterte_rezepte:
                    continue
                    
                # Nur Kochdauer-Filter beibehalten
                if max_kochdauer is not None:
                    rezept_kochdauer = rezept.get("kochdauer_minuten", 60)
                    if rezept_kochdauer > max_kochdauer:
                        continue
                        
                rezept["saisonalitaets_info"] = berechne_saisonalitaets_score(rezept, monat)
                gefilterte_rezepte.append(rezept)
                
                if len(gefilterte_rezepte) >= anzahl:
                    break
        
        # Zufällige Auswahl
        if len(gefilterte_rezepte) > anzahl:
            gefilterte_rezepte = random.sample(gefilterte_rezepte, anzahl)
        
        print(f"Finale Auswahl: {len(gefilterte_rezepte)} Rezepte")
        return jsonify(gefilterte_rezepte)
        
    except Exception as e:
        print(f"Fehler in rezepte_gefiltert: {e}")
        return jsonify({"error": str(e)}), 500
        

@app.route("/saisoninfo", methods=["POST"])
def saisoninfo():
    """Berechnet Saisonalitäts-Info für einzelnes Rezept"""
    daten = request.get_json()
    rezept_id = daten.get("rezept_id")
    monat = daten.get("monat")
    
    rezept = next((r for r in rezepte if r["id"] == rezept_id), None)
    if not rezept:
        return jsonify({"error": "Rezept nicht gefunden"}), 404
    
    saison_info = berechne_saisonalitaets_score(rezept, monat)
    return jsonify(saison_info)


@app.route("/alle-rezepte")
def alle_rezepte():
    """Gibt alle verfügbaren Rezepte zurück (ohne Filter)"""
    try:
        # Optional: Nur die wichtigsten Felder für Performance
        vereinfachte_rezepte = []
        for rezept in rezepte:
            vereinfachte_rezepte.append({
                "id": rezept.get("id"),
                "name": rezept.get("name"),
                "kochdauer_minuten": rezept.get("kochdauer_minuten"),
                "zutaten": rezept.get("zutaten", [])  # Für Saisonalitäts-Berechnung
            })
        
        print(f"Alle Rezepte gesendet: {len(vereinfachte_rezepte)}")
        return jsonify(vereinfachte_rezepte)
    except Exception as e:
        print(f"Fehler in alle_rezepte: {e}")
        return jsonify({"error": str(e)}), 500


logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

@app.before_request
def before_request():
    logging.info('Request: %s', request)

@app.after_request
def after_request(response):
    logging.info('Response: %s', response)
    return response

@app.errorhandler(404)
def page_not_found(e):
    logging.error('404 error: %s', e)
    return 'This page does not exist', 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error('500 error: %s', e)
    return 'Internal server error', 500


if __name__ == "__main__":
    app.run(debug=True)