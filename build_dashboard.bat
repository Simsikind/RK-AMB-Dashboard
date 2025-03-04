del dist\Ambulanz-Dashboard.exe
rmdir dist
del Ambulanz-Dashboard.exe
pyinstaller --onefile --icon=image_files/RK.ico -n "Ambulanz-Dashboard" main.py
move dist\Ambulanz-Dashboard.exe
del dist\Ambulanz-Dashboard.exe
rmdir dist


del dist\Patienten-Anzeige.exe
rmdir dist
del Patienten-Anzeige.exe
pyinstaller --onefile --icon=image_files/RK.ico -n "Patienten-Anzeige" patient_viewer.py
move dist\Patienten-Anzeige.exe
del dist\Patienten-Anzeige.exe
rmdir dist
pause