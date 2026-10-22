@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
where py >nul 2>nul
if errorlevel 1 (set "VENTAS_BOOTSTRAP=python") else (set "VENTAS_BOOTSTRAP=py")
if not exist ".venv\Scripts\python.exe" "%VENTAS_BOOTSTRAP%" -m venv .venv
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 goto error
".venv\Scripts\python.exe" src\train.py
if errorlevel 1 goto error
echo Preparacion terminada. Ejecuta iniciar.bat.
pause
exit /b 0
:error
echo No se completo la preparacion. Revisa el mensaje anterior.
pause
exit /b 1
