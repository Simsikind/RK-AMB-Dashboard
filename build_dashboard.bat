@echo off
echo Starte Buildprozess...

REM Erstelle build Ordner, falls nicht vorhanden
if not exist build mkdir build

REM main.pyzu Ambulanz-Dashboard.exe
pyinstaller --onefile --distpath build --name Ambulanz-Dashboard main.py

REM patient_viewer.py zu Patientenanzeige.exe
pyinstaller --onefile --distpath build --name Patientenanzeige patient_viewer.py

REM Pinmanager.py zu PIN_Manager.exe
pyinstaller --onefile --distpath build --name PIN_Manager Pinmanager.py

REM Lösche automatisch alle .spec-Dateien im aktuellen Verzeichnis
del /q *.spec

REM Entferne __pycache__-Ordner
rmdir /s /q __pycache__

echo Build abgeschlossen. EXE-Dateien befinden sich im 'build'-Ordner.
pause