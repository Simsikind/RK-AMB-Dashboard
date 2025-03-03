del dist\Ambulanz-Dashboard.exe
rmdir dist
del Ambulanz-Dashboard.exe
pyinstaller --onefile --icon=image_files/RK.ico -n "Ambulanz-Dashboard" main.py
move dist\Ambulanz-Dashboard.exe
del dist\Ambulanz-Dashboard.exe
rmdir dist
pause