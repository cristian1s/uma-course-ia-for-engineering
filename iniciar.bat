@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if exist ".venv\Scripts\python.exe" (
  set "VENTAS_PYTHON=.venv\Scripts\python.exe"
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    set "VENTAS_PYTHON=python"
  ) else (
    set "VENTAS_PYTHON=py"
  )
)
"%VENTAS_PYTHON%" -c "import fastapi, uvicorn, pandas, sklearn, joblib" >nul 2>nul
if errorlevel 1 (
  echo Faltan dependencias. Ejecuta primero preparar.bat.
  pause
  exit /b 1
)
if not exist "models\modelo.pkl" goto entrenar
if not exist "models\modelo_nuevo.pkl" goto entrenar
if not exist "models\metadata.json" goto entrenar
goto ejecutar
:entrenar
"%VENTAS_PYTHON%" src\train.py
if errorlevel 1 (
  pause
  exit /b 1
)
:ejecutar
echo.
echo Panel: http://127.0.0.1:8000/panel
echo API:   http://127.0.0.1:8000/docs
echo Mantener esta ventana abierta. Para detener: Ctrl+C.
"%VENTAS_PYTHON%" src\serve.py
pause
