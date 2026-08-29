let aktuelleGerichte = [];
let alleRezepte = [];

async function ladeAlleRezepte() {
    try {
        const response = await fetch("/alle-rezepte");
        alleRezepte = await response.json();
        console.log("Alle Rezepte geladen:", alleRezepte.length);
        renderGerichte();
    } catch (error) {
        console.error("Fehler beim Laden aller Rezepte:", error);
    }
}

// Einfache Zufallsfunktion (für Backup/Tests)
function ladeZufall() {
    console.log("Button 'Woche planen' wurde geklickt!");
    fetch("/zufall")
        .then(res => res.json())
        .then(data => {
            aktuelleGerichte = data;
            renderGerichte();
        })
        .catch(error => console.error("Fehler beim Laden der Gerichte:", error));
}

// HAUPTFUNKTION: Lädt gefilterte Gerichte
function ladeGefilterteGerichte() {
    console.log("Lade gefilterte Gerichte...");
    
    // Aktuelle Filtereinstellungen sammeln
    const filterData = {
        saisonalitaet: document.getElementById("filter-saisonalitaet").checked,
        max_kochdauer: document.getElementById("filter-kochdauer").value || null,
        monat: document.getElementById("filter-monat").value || null,
        anzahl: 5
    };
    
    fetch("/rezepte-gefiltert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(filterData)
    })
    .then(res => res.json())
    .then(data => {
        aktuelleGerichte = data;
        renderGerichte(); // Verwendet die erweiterte Render-Funktion
    })
    .catch(error => console.error("Fehler beim Laden der gefilterten Gerichte:", error));
}

// EINZIGE Render-Funktion mit Saisonalitäts-Anzeige (siehe unten)

// Neue Funktion: Zeige Auswahl-Dropdown
function zeigeAuswahl(index) {
    const dropdown = document.getElementById(`auswahl-dropdown-${index}`);
    
    // Schließe alle anderen Dropdowns
    document.querySelectorAll('.auswahl-dropdown').forEach(dd => {
        if (dd.id !== `auswahl-dropdown-${index}`) {
            dd.style.display = 'none';
        }
    });
    
    if (dropdown.style.display === "none") {
        dropdown.style.display = "block";
        fuelleRezeptListe(index);
    } else {
        dropdown.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    ladeAlleRezepte();
});

// Neue Variable für Pagination
let aktuelleLadeanzahl = {};

// Überarbeitete Funktion: Fülle Rezeptliste (ohne Suchfeld)
function fuelleRezeptListe(index, anzahlLaden = 10, istInitial = false) {
    const liste = document.getElementById(`rezept-liste-${index}`);
    
    // Initialisiere Ladeanzahl für diesen Index falls noch nicht vorhanden
    if (!aktuelleLadeanzahl[index]) {
        aktuelleLadeanzahl[index] = 0;
    }
    
    // Beim ersten Laden Liste leeren
    if (istInitial) {
        liste.innerHTML = "";
        aktuelleLadeanzahl[index] = 0;
    }
    // Sortiere alle Rezepte alphabetisch
    const sortierteRezepte = [...alleRezepte].sort((a, b) => a.name.localeCompare(b.name));
    
    // Berechne Start- und Endindex
    const startIndex = aktuelleLadeanzahl[index];
    const endIndex = startIndex + anzahlLaden;
    const rezepteZumLaden = sortierteRezepte.slice(startIndex, endIndex);
    
    // Füge Rezepte zur Liste hinzu
    rezepteZumLaden.forEach(rezept => {
        const rezeptItem = document.createElement("div");
        rezeptItem.className = "rezept-item";
        
        const kochdauer = rezept.kochdauer_minuten || "unbekannt";
        const istAktuell = aktuelleGerichte[index] && aktuelleGerichte[index].id === rezept.id;
        
        rezeptItem.innerHTML = `
            <div class="rezept-info">
                <span class="rezept-name ${istAktuell ? 'aktuell-gewählt' : ''}">${rezept.name}</span>
                <span class="rezept-dauer">⏱️ ${kochdauer} Min</span>
            </div>
        `;
        
        // Click-Handler für Rezeptauswahl
        rezeptItem.onclick = () => wähleRezept(index, rezept);
        
        liste.appendChild(rezeptItem);
    });
    
    // Aktualisiere Ladeanzahl
    aktuelleLadeanzahl[index] = endIndex;
    
    // Entferne alten "Mehr laden" Button falls vorhanden
    const alterButton = document.getElementById(`mehr-laden-${index}`);
    if (alterButton) {
        alterButton.remove();
    }
    
    // Füge "Mehr laden" Button hinzu, falls noch mehr Rezepte vorhanden
    if (endIndex < sortierteRezepte.length) {
        const mehrLadenButton = document.createElement("div");
        mehrLadenButton.id = `mehr-laden-${index}`;
        mehrLadenButton.className = "mehr-laden-button";
        
        const button = document.createElement("button");
        button.textContent = `Mehr laden (${sortierteRezepte.length - endIndex} weitere)`;
        button.addEventListener("click", () => ladeMehrRezepte(index));

            //mehrLadenButton.innerHTML = `
               // <button onclick="ladeMehrRezepte(${index})">
               // Mehr laden (${sortierteRezepte.length - endIndex} weitere)
               // </button>
            //`;
        mehrLadenButton.appendChild(button);
        liste.appendChild(mehrLadenButton);
    }
}

// Neue Funktion: Lade weitere Rezepte
function ladeMehrRezepte(index) {
    fuelleRezeptListe(index, 10);
}

// Überarbeitete renderGerichte Funktion (ohne Suchfeld im HTML)
function renderGerichte() {
    const container = document.getElementById("gerichte");
    container.innerHTML = "";

    // Fallback für einfache Gerichte ohne erweiterte Daten
    aktuelleGerichte.forEach((gericht, index) => {
        const saisonInfo = gericht.saisonalitaets_info || {};
        const saisonSymbol = getSaisonSymbol(saisonInfo.bewertung);
        const kochdauer = gericht.kochdauer_minuten || "unbekannt";
        
        const div = document.createElement("div");
        div.className = "gericht-item";
        div.innerHTML = `
            <div class="gericht-header">
                <strong>Tag ${index + 1}:</strong> ${gericht.name}
                <span class="saison-indicator" title="Saisonalität: ${saisonInfo.bewertung || 'unbekannt'}">${saisonSymbol}</span>
            </div>
            <div class="gericht-details">
                <span class="kochdauer">⏱️ ${kochdauer} Min</span>
                <span class="saison-score">🌱 ${Math.round(saisonInfo.score || 0)}% saisonal</span>
            </div>
            <div class="gericht-aktionen">
                <button onclick="tauscheGericht(${index})">Tauschen</button>
                <button onclick="zeigeAuswahl(${index})">Auswahl</button>
                <button onclick="zeigeSaisonDetails(${index})">Saison-Details</button>
            </div>
            <div id="auswahl-dropdown-${index}" class="auswahl-dropdown" style="display: none;">
                <div class="dropdown-header">
                    <span class="dropdown-titel">Rezept auswählen</span>
                    <button onclick="schließeAuswahl(${index})">×</button>
                </div>
                <div id="rezept-liste-${index}" class="rezept-liste">
                    <!-- Wird dynamisch gefüllt -->
                </div>
            </div>
            <div id="saison-details-${index}" class="saison-details-container" style="display: none;">
                ${renderSaisonDetails(saisonInfo)}
            </div>
        `;
        container.appendChild(div);
    });
}

// Neue Funktion: Schließe Auswahl-Dropdown (erweitert um Reset der Ladeanzahl)
function schließeAuswahl(index) {
    document.getElementById(`auswahl-dropdown-${index}`).style.display = "none";
    // Reset der Ladeanzahl für nächstes Öffnen
    aktuelleLadeanzahl[index] = 0;
}

// Die wähleRezept Funktion bleibt unverändert
async function wähleRezept(index, rezept) {
    try {
        // Berechne Saisonalitäts-Info für das gewählte Rezept
        const monat = document.getElementById("filter-monat").value || null;
        const response = await fetch("/saisoninfo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                rezept_id: rezept.id, 
                monat: monat 
            })
        });
        
        const saisonInfo = await response.json();
        rezept.saisonalitaets_info = saisonInfo;
        
        // Ersetze das Gericht
        aktuelleGerichte[index] = rezept;
        
        // Schließe Dropdown und aktualisiere Anzeige
        schließeAuswahl(index);
        renderGerichte();
        
        console.log(`Rezept gewählt: ${rezept.name} für Tag ${index + 1}`);
        
    } catch (error) {
        console.error("Fehler beim Wählen des Rezepts:", error);
        // Fallback: Setze Rezept ohne Saisoninfo
        aktuelleGerichte[index] = rezept;
        schließeAuswahl(index);
        renderGerichte();
    }
}
// EINZIGE Tausch-Funktion mit Filtern
function tauscheGericht(index) {
    const filterData = {
        saisonalitaet: document.getElementById("filter-saisonalitaet").checked,
        max_kochdauer: document.getElementById("filter-kochdauer").value || null,
        monat: document.getElementById("filter-monat").value || null,
        anzahl: 1
    };
    
    fetch("/rezepte-gefiltert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(filterData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.length > 0) {
            // Wähle ein Gericht aus, das nicht bereits in der Liste ist
            const verfügbareGerichte = data.filter(g => 
                !aktuelleGerichte.some(ag => ag.id === g.id)
            );
            
            if (verfügbareGerichte.length > 0) {
                aktuelleGerichte[index] = verfügbareGerichte[0];
            } else {
                aktuelleGerichte[index] = data[0]; // Fallback
            }
            
            renderGerichte();
        }
    })
    .catch(error => console.error("Fehler beim Tauschen des Gerichts:", error));
}

// Hilfsfunktionen
function getSaisonSymbol(bewertung) {
    switch(bewertung) {
        case "gut": return "🟢";
        case "mittel": return "🟡";
        case "schlecht": return "🔴";
        default: return "⚪";
    }
}

function renderSaisonDetails(saisonInfo) {
    if (!saisonInfo.details) return "Keine Details verfügbar";
    
    return `
        <h4>Saisonalitäts-Details:</h4>
        <ul>
            ${saisonInfo.details.map(detail => `<li>${detail}</li>`).join('')}
        </ul>
        <p><strong>Score:</strong> ${saisonInfo.treffer || 0} von ${saisonInfo.gesamt || 0} Zutaten sind saisonal</p>
    `;
}

function zeigeSaisonDetails(index) {
    const detailsDiv = document.getElementById(`saison-details-${index}`);
    if (detailsDiv.style.display === "none") {
        detailsDiv.style.display = "block";
    } else {
        detailsDiv.style.display = "none";
    }
}

// Schließe Dropdowns wenn außerhalb geklickt wird
document.addEventListener('click', function(event) {
    if (!event.target.closest('.auswahl-dropdown') && !event.target.closest('button[onclick*="zeigeAuswahl"]')&& !event.target.closest('.mehr-laden-button')) {
        document.querySelectorAll('.auswahl-dropdown').forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    }
});

let anzahlTage = 3; // Standardwert

function aktualisiereAnzahlTage() {
    const auswahl = document.getElementById("tage-auswahl").value;
    anzahlTage = parseInt(auswahl, 10);
    generiereRezepte(); // Funktion zum Erzeugen der Rezeptideen
}
function generiereRezepte() {
    aktuelleGerichte = []; // Reset
    const zufälligeRezepte = zieheZufälligeRezepte(anzahlTage);
    aktuelleGerichte = zufälligeRezepte;
    renderGerichte(); // erzeugt die Anzeige
}


// Einkaufsliste und Speichern
function generiereEinkaufsliste() {
    fetch("/Einkaufsliste", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gerichte: aktuelleGerichte })
    })
    .then(res => res.json())
    .then(liste => {
        const div = document.getElementById("einkaufsliste");
        div.innerHTML = "<h2>Einkaufsliste</h2>";
        for (let kategorie in liste) {
            div.innerHTML += `<strong>${kategorie}</strong><ul>`;
            liste[kategorie].forEach(zutat => {
                div.innerHTML += `<li>${zutat}</li>`;
            });
            div.innerHTML += `</ul>`;
        }
    })
    .catch(error => console.error("Fehler beim Generieren der Einkaufsliste:", error));
}

function speichereWoche() {
    fetch("/speichere-woche", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gerichte: aktuelleGerichte })
    })
    .then(res => res.json())
    .then(data => {
        alert("Woche gespeichert!");
    })
    .catch(error => console.error("Fehler beim Speichern der Woche:", error));
}

// Initialisierung
function initializeFilters() {
    // Aktuellen Monat als Standard setzen
    const monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
                   'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
    const aktuellerMonat = monate[new Date().getMonth()];
    const monatSelect = document.getElementById("filter-monat");
    if (monatSelect) {
        monatSelect.value = aktuellerMonat;
    }
    
    // Event Listener für Filter-Änderungen (optional - für automatisches Neuladen)
    // document.getElementById("filter-saisonalitaet").addEventListener("change", ladeGefilterteGerichte);
    // document.getElementById("filter-kochdauer").addEventListener("change", ladeGefilterteGerichte);
    // document.getElementById("filter-monat").addEventListener("change", ladeGefilterteGerichte);
}

// Beim Laden der Seite initialisieren
document.addEventListener('DOMContentLoaded', initializeFilters);