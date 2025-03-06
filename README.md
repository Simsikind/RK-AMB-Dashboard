# Ambulanz-Dashboard Bedienungsanleitung

## Version 1.3

Ein Organisationsprogramm für Ambulanzen  
Geschrieben von Simon B.  
März 2025  

---

## Inhaltsverzeichnis

1. [Einführende Worte](#einführende-worte)
2. [Systemvoraussetzungen](#systemvoraussetzungen)
   - Standard
   - Für Nerds
3. [Installation](#installation)
4. [Start des Programms](#start-des-programms)
   - Standard
   - Für Nerds
5. [Benutzeroberfläche](#benutzeroberfläche)
6. [Ambulanzdatenverwaltung](#ambulanzdatenverwaltung)
   - Ambulanzdaten konfigurieren
   - Ambulanzdaten speichern (als)
   - Ambulanzdaten öffnen
7. [Patientenverwaltung](#patientenverwaltung)
   - Patienten erstellen
   - Patienten bearbeiten
   - Die Patientenliste
   - Sortieren
   - Filtern
8. [Auslastung](#auslastung)
9. [Sonstige Funktionen](#sonstige-funktionen)
   - Statistik anzeigen
   - Patientenliste exportieren
10. [Tastaturbefehle](#tastaturbefehle)
11. [Multi-Computer-System](#multi-computer-system)
    - NAS
    - Windows-Filesharing
12. [Abschließende Worte](#abschließende-worte)

---

## Einführende Worte

Das "Ambulanz-Dashboard" wurde entwickelt, um den Workflow in Behandlungsstellen zu optimieren. 
Es ersetzt Microsoft Excel für die Sichtung und Zuordnung von Patienten. 

Dieses Dokument beschreibt die Nutzung des Programms.

Kontakt bei Fragen: **simonios17@gmail.com**

---

## Systemvoraussetzungen

### Standard
- Windows 10
- Läuft ohne weitere Anpassungen

### Für Nerds
- Andere Betriebssysteme benötigen Python 3
- Notwendige Libraries folgen
- Getestet auf Raspbian (Raspberry Pi 3B+)
- 

---

## Installation

1. **Download:**
   - Das Programm kann unter `github.com/Simsikind/RK-AMB-Dashboard` heruntergeladen werden.
   - Klicke auf "Code" > "Download ZIP".
2. **Entpacken:**
   - Der heruntergeladene Ordner muss entpackt werden.
   - Der Speicherort sollte gemerkt werden.

---

## Start des Programms

### Standard
- **Windows:** `Ambulanz-Dashboard.exe` starten.

### Für Nerds
- **Linux/Mac:** `main.py` mit Python 3 starten.
- Programm benötigt 30-45 Sekunden zum Starten.

---

## Benutzeroberfläche

Die UI gliedert sich in:
1. Ambulanzdaten-Bereich
2. Patientendetail-Bereich
3. Patientenliste
4. Betreuungs-Bereich
5. Auslastungsanzeige

---

## Ambulanzdatenverwaltung

### Ambulanzdaten konfigurieren
- Über `Menü öffnen` > `Daten konfigurieren` können Ambulanzdaten eingegeben werden.

### Ambulanzdaten speichern (als)
- Im Menü auf `Daten speichern als` klicken.
- Datei mit `.dat` speichern.

### Ambulanzdaten öffnen
- Gespeicherte Datei kann über `Daten lesen` geladen werden.

---

## Patientenverwaltung

### Patienten erstellen
- Roter Knopf `[Neuer Patient]` klicken.

### Patienten bearbeiten
- Pflichtfelder: Behandlungszeit, Platz, Einsatzende.

### Die Patientenliste
- **Sortieren:** Nach jeder Spalte möglich.
- **Filtern:** Über `[Filter Menü öffnen]` möglich.

---

## Auslastung

- Wird in % angezeigt.
- Details über `[Auslastung-Details]` abrufbar.
- Farben:
  - **Grün:** <50%
  - **Gelb:** 50%-80%
  - **Rot:** >80%

---

## Sonstige Funktionen

### Statistik anzeigen
- Zeigt NACA-Scores der Patienten an.

### Patientenliste exportieren
- Export als `.csv` Datei.
- Speicherort: `\Userdata\Export`

---

## Tastaturbefehle

- **Universell:**
  - Bestätigen: `<Return>`
  - Abbrechen: `<Escape>`
  - Vollbildmodus: `<F11>`
- **Datenverwaltung:**
  - Laden: `<Ctrl-o>`
  - Speichern: `<Ctrl-s>`
- **Patientenverwaltung:**
  - Neuer Patient: `<Ctrl-n>`
  - Bearbeiten: `<Ctrl-e>`
  - Löschen: `<Ctrl-Delete>`
- **Filter:**
  - Nur aktive Patienten: `<Ctrl-a>`
  - Filter zurücksetzen: `<Ctrl-r>`

---

## Multi-Computer-System

### NAS
- Programmordner auf NAS speichern.
- Zugriff über Windows-Netzwerk.

### Windows-Filesharing
- Programmordner freigeben:
  1. Rechtsklick > `Zugriff gewähren auf` > `Bestimmte Personen`
  2. `Jeder` hinzufügen
  3. Berechtigung auf `Lesen/Schreiben` setzen
  4. Freigabe aktivieren
- Zugriff über Netzwerk-Explorer möglich.

---

## Abschließende Worte

Für Fragen, Anmerkungen oder Verbesserungsvorschläge: **simonios17@gmail.com**

Dieses Projekt ist Open-Source und kann auf GitHub verbessert werden. 

Viel Spaß mit dem Ambulanz-Dashboard!

**Liebe Grüße,**  
Simon B.
