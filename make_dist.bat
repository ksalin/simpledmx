@echo off
echo If pyinstaller not found, run: pip install pyinstaller
pyinstaller --onefile --windowed --name "Simple DMX" --icon=simpledmx_icon.ico simpledmx.py --add-data "simpledmx_icon.png;."