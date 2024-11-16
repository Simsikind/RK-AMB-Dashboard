# Patientenverwaltung - Ambulanz Dashboard

Dieses Projekt bietet ein Dashboard zur Verwaltung und Bearbeitung von Patientendaten im Zuge einer Ambulanz. Die Anwendung ermöglicht das Hinzufügen, Bearbeiten und Exportieren von Patienten- und Betreuungsdaten über eine grafische Benutzeroberfläche (GUI), die mit Python und Tkinter erstellt wurde.

## Installation

1. **Projekt herunterladen**:
   - Besuchen Sie das [GitHub-Repository](https://github.com/Simsikind/RK-AMB-Dashboard) und laden Sie das Projekt als `.zip` herunter.
   - Entpacken Sie das `.zip`-Archiv an einem gewünschten Ort auf Ihrem Computer.

2. **Anwendung starten**:
   - Die Anwendung kann über die enthaltene EXE-Datei gestartet werden.
   - Alternativ können Sie den Quellcode ausführen (siehe dazu den Punkt **Anwendung starten**).


3. **Anwendung auf Android starten**:  
   - Sie können das Dashboard auch auf einem Android-Gerät verwenden. Details zur Ausführung auf Android finden Sie unter dem Punkt **Anwendung starten – Auf Android mit PyDroid 3**.

## Anwendung starten

1. **Über die EXE-Datei**: Doppelklicken Sie die bereitgestellte EXE-Datei, um das Programm zu starten.
2. **Auf Android mit PyDroid 3**:  
   Falls Sie das Dashboard auf einem Android-Gerät verwenden möchten, öffnen Sie die Datei `Android-AMB-Dashboard.py` in der App [PyDroid 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3) und führen Sie sie aus. PyDroid 3 ist eine Python-IDE für Android, die es ermöglicht, Python-Skripte direkt auf Ihrem Smartphone oder Tablet auszuführen.

   **Hinweise zur Verwendung auf Android**:
   - Die Funktionalität des GUIs kann aufgrund der Touchscreen-Steuerung leicht abweichen. Zum Beispiel können Fenster möglicherweise nicht skaliert werden.
   - Stellen Sie sicher, dass genügend Speicherplatz auf Ihrem Gerät vorhanden ist, insbesondere wenn Sie große Datenmengen exportieren oder laden.
3. **Über den Quellcode**: Falls Sie die Anwendung aus dem Quellcode starten möchten, führen Sie `main.py` aus:
    ```bash
    python main.py
    ```

## Anwendung verwenden

**WICHTIG**: Vor der Verwendung der Anwendung sollten die **Ambulanzdaten gesetzt** werden. Dies kann auf zwei Arten geschehen:
   - Ambulanzdaten manuell eingeben und anschließend speichern. Hierbei ist zu beachten, dass der Dateiname unbedingt mit `.dat` erweitert werden muss.
   - Ambulanzdaten aus einer Datei laden, die bereits die notwendigen Informationen enthält.

### Hauptfunktionen

1. **Patienten hinzufügen/löschen**:
   - **Neuer Patient**: Fügt einen neuen Patienten mit einer fortlaufenden, eindeutigen Ablagenummer (ID) zur Liste hinzu.
   - **Patient löschen**: Entfernt den zuletzt hinzugefügten Patienten aus der Liste.

2. **Patientendaten bearbeiten**:
   - Wählen Sie einen Patienten aus und klicken Sie auf **Pat Bearbeiten**, um Details wie Alarmzeit, Berufungsgrund, Berufungsort, Zeit auf Behandlung, NACA-Wert, Abtransport-Organisation und andere Felder zu ändern.

3. **Navigation**:
   - Mit den Buttons `>` und `<` kann zwischen Patienten gewechselt werden, um deren Daten anzuzeigen.

4. **Betreuungen hinzufügen/löschen**:
   - **Neue Betreuung**: Fügt eine Betreuung zur Gesamtliste hinzu.
   - **Betreuung Löschen**: Entfernt die zuletzt hinzugefügte Betreuung.

5. **Statistik**:
   - Um eine Statistik der Patienten anzuzeigen, klicken Sie auf **Statistik anzeigen**

6. **Daten exportieren und speichern**:
   - **Daten in Datei speichern**: Speichert alle Ambulanzdaten in einer `.dat`-Datei.
   - **Daten aus Datei laden**: Lädt Ambulanz- und Patientendaten aus einer `.dat`-Datei.
   - **Patientenliste exportieren**: Exportiert die aktuelle Patientenliste in eine CSV-Datei im Ordner `Export`.

7. **Manuelle Einstellungen der Ambulanzdaten**:
   - Über das Menü **Daten manuell Setzen** können die Ambulanznummer, der Name und das Datum manuell eingestellt werden.

### Weitere Hinweise

- **Ordnerstrukturen**: 
  - Ein Ordner `Export` wird für den CSV-Export der Patientenliste erstellt.
  - Ein Ordner `PatDat` wird für die Speicherung und den Import von Patientenlisten angelegt.
  
- **Datenstrukturen**:
  - Patienten werden in einer Liste (`Patlist`) gespeichert, und jede Patienteninstanz wird durch die `Patient`-Klasse in `functions.py` definiert.

## Bekannte Einschränkungen

- **Datensicherung**: Alle Patientendaten werden lokal als Binärdateien gespeichert und müssen manuell geladen und gespeichert werden.
- **Datenintegrität**: Die Anwendung stellt sicher, dass keine Patientendaten als Textfile gespeichert werden. Daher sind die Daten nur mit dieser Anwendung verwendbar. Trotzdem dürfen in die Textfelder keine Daten eingetragen werden, die Drittparteien ein Zuordnen des Datensatzes zu realen Personen ermöglichen. Die Verantwortung hierfür liegt beim Benutzer.

## Voraussetzungen & Anpassungen

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
```
Die EXE-Datei kann dann einfach mit dem folgenden Befehl generiert werden:
´´´bash
build_dashboard
´´´
 
