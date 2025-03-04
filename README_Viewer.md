# Ambulanz-Dashboard Echtzeit

Dieses Projekt ist ein Echtzeit-Dashboard zur Verwaltung und Anzeige von Patientendaten in einem Ambulanz-Setting. Das Dashboard wurde mit Python und Tkinter für die grafische Benutzeroberfläche erstellt.

## Funktionen

- Anzeige einer Liste von Patienten mit Details wie Nummer, Behandlungszeit, Behandlungsort, Sichtungskategorie, NACA-Score, Alarmgrund und Kommentaren.
- Farblich gekennzeichnete Patientenliste basierend auf der Sichtungskategorie.
- Echtzeit-Updates der Patientendaten aus einer `.ambdat`-Datei.
- Anzeige der Auslastungsstatistiken für verschiedene Behandlungsplätze.
- Scrollbare Patientenliste und Auslastungsstatistiken.
- Setzen der Ambulanznummer und Initialisierung der Daten aus einer `.dat`-Datei.

## Anforderungen

- Python 3.x
- Tkinter (normalerweise in Python enthalten)
- `pickle`-Modul (normalerweise in Python enthalten)
- `os`, `re`, `time`-Module (normalerweise in Python enthalten)

## Installation

1. Klonen Sie das Repository oder laden Sie die Datei `patient_viewer.py` herunter.
2. Stellen Sie sicher, dass Python 3.x auf Ihrem System installiert ist.
3. Installieren Sie alle fehlenden Abhängigkeiten mit `pip` (falls erforderlich).

## Verwendung

1. Starten Sie die Anwendung über die ausführbare Datei `Patienten-Anzeige.exe`:
   ```sh
   start Patienten-Anzeige.exe
   ```

2. Alternativ können Sie das Skript `patient_viewer.py` direkt ausführen:
   ```sh
   python patient_viewer.py
   ```

3. Das Hauptfenster des Dashboards wird geöffnet.

4. Klicken Sie auf die Schaltfläche "Ambulanznummer setzen", um eine `.dat`-Datei mit den Ambulanzdaten auszuwählen.

5. Die Patientenliste und die Auslastungsstatistiken werden angezeigt und in Echtzeit aktualisiert.