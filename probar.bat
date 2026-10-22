@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if exist ".venv\Scripts\python.exe" (set "VENTAS_PYTHON=.venv\Scripts\python.exe") else (set "VENTAS_PYTHON=py")
"%VENTAS_PYTHON%" -m unittest discover -s tests -v
pause
