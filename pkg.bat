pyinstaller --noconfirm --onedir --windowed --icon "icons/logo.ico" --add-data "icons;icons/"  "cube-shell.py"
cd dist/cube-shell/_internal
move icons  ..