# Patientenverwaltung - Ambulanz Dashboard

Dieses Projekt bietet ein Dashboard zur Verwaltung und Bearbeitung von Patientendaten in einer Ambulanz. Die Anwendung ermöglicht das Hinzufügen, Bearbeiten und Exportieren von Patienten- und Betreuungsdaten über eine grafische Benutzeroberfläche (GUI), die mit Python und Tkinter erstellt wurde.

## Anwendung starten

1. **Über die EXE-Datei**: Doppelklicken Sie die bereitgestellte EXE-Datei, um das Programm zu starten.
2. **Über den Quellcode**: Falls Sie die Anwendung aus dem Quellcode starten möchten, führen Sie `main.py` aus:
    ```bash
    python main.py
    ```

## Anwendung verwenden

**WICHTIG**: Vor der Verwendung der Anwendung sollten die **Ambulanzdaten gesetzt** werden. Dies kann auf zwei Arten geschehen:
   - Ambulanzdaten manuell eingeben und anschließend speichern.
   - Ambulanzdaten aus einer Datei laden, die bereits die notwendigen Informationen enthält.

### Hauptfunktionen

1. **Patienten hinzufügen/löschen**:
   - **Neuer Patient**: Fügt einen neuen Patienten mit einer eindeutigen ID zur Liste hinzu.
   - **Patient löschen**: Entfernt den zuletzt hinzugefügten Patienten aus der Liste.

2. **Patientendaten bearbeiten**:
   - Wählen Sie einen Patienten aus und klicken Sie auf **Pat Bearbeiten**, um Details wie Alarmzeit, Berufungsgrund, Berufungsort, Zeit auf Behandlung, NACA-Wert, Abtransport-Organisation und andere Felder zu ändern.

3. **Navigation**:
   - Mit den Buttons `>` und `<` kann zwischen Patienten gewechselt werden, um deren Daten anzuzeigen.

4. **Betreuungen hinzufügen/löschen**:
   - **Neue Betreuung**: Fügt eine Betreuung zur Gesamtliste hinzu.
   - **Betreuung Löschen**: Entfernt die zuletzt hinzugefügte Betreuung.

5. **Daten exportieren und speichern**:
   - **Daten in Datei speichern**: Speichert alle Ambulanzdaten in einer `.dat`-Datei.
   - **Daten aus Datei laden**: Lädt Ambulanz- und Patientendaten aus einer `.dat`-Datei.
   - **Patientenliste exportieren**: Exportiert die aktuelle Patientenliste in eine CSV-Datei im Ordner `Export`.

6. **Manuelle Einstellungen der Ambulanzdaten**:
   - Über das Menü **Daten manuell Setzen** können die Ambulanznummer, der Name und das Datum manuell eingestellt werden.

### Weitere Hinweise

- **Ordnerstrukturen**: 
  - Ein Ordner `Export` wird für den CSV-Export der Patientenliste erstellt.
  - Ein Ordner `PatDat` wird für die Speicherung und den Import von Patientenlisten angelegt.
  
- **Datenstrukturen**:
  - Patienten werden in einer Liste (`Patlist`) gespeichert, und jede Patienteninstanz wird durch die `Patient`-Klasse in `functions.py` definiert.

## Bekannte Einschränkungen

- **Datensicherung**: Alle Patientendaten werden lokal als Binärdateien gespeichert und müssen manuell geladen und gespeichert werden.
- **Datenintegrität**: Die Anwendung stellt sicher, dass keine Patientendaten ohne Bestätigung gelöscht werden, jedoch werden die Änderungen direkt in den Objekten vorgenommen und sind nach einer Bestätigung unwiderruflich.

## Voraussetzungen

Falls Sie den Quellcode anpassen und die EXE-Datei neu erstellen möchten, sind folgende Voraussetzungen erforderlich:

- **Python** 3.6 oder höher
- Module:
  - `tkinter`
  - `pickle`
  - `csv`
  - `os`
  - `re`

Zusätzlich wird **PyInstaller** benötigt, um die EXE-Datei zu generieren:
```bash
pip install pyinstaller
