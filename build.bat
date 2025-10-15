@echo off
REM build.bat — genera el EXE con PyInstaller (todo incluido)
REM Requisitos (una sola vez):
REM   pip install -r requirements.txt
REM   pip install pyinstaller
SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
pyinstaller build.spec
echo.
echo ===========================================
echo  EXE en: dist\AgendaRadicador.exe
echo ===========================================
pause
