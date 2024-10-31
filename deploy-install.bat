@echo off & setlocal enabledelayedexpansion
rem cube-shell windows exe.bat

rem dos utf-8 encode
chcp 65001

REM Step 3: Create tunnel.json file
echo 3: Creating tunnel.json file...
echo {} > deploy\cube-shell.dist\conf\tunnel.json

REM Step 4: Delete config.dat file
echo 4: Deleting config.dat file...
del /Q deploy\cube-shell.dist\conf\config.dat

REM Step 5: Deploy using Inno Setup
echo 5: Deploying using Inno Setup...
iscc installer.iss

echo Done!
pause
goto :eof