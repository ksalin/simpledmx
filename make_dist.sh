echo If pyinstaller not found, run: pip install pyinstaller
pyinstaller --onefile --windowed --name "Simple DMX" --icon=simpledmx_icon.png simpledmx.py --add-data "simpledmx_icon.png:."