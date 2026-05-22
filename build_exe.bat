@echo off
title Compilazione InGeoLab in EXE standalone
echo =======================================================
echo   Compilatore Automatico per PolaresInvert.py
echo =======================================================
echo.
echo 1. Controllo e aggiornamento di pip...
python -m pip install --upgrade pip

echo.
echo 2. Installazione di PyInstaller...
pip install pyinstaller

echo.
echo 3. Compilazione del file .exe (Inclusione forzata Backend)...
echo Questo processo puo richiedere diversi minuti. Attendi...
pyinstaller --onefile --noconsole --collect-all pygimli --collect-all matplotlib --collect-data matplotlib --hidden-import matplotlib.backends.backend_tkagg --hidden-import matplotlib.backends.backend_agg PolaresInvert.py

echo.
echo =======================================================
echo   PROCEDURA COMPLETATA!
echo =======================================================
echo Se non ci sono stati errori, trovi il tuo file .exe
echo all'interno della cartella chiamato 'dist'.
echo.
pause