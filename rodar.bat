@echo off
REM Sobe a aplicacao localmente com SQLite (sem Docker) e abre o navegador.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instale em https://www.python.org marcando "Add Python to PATH".
  pause
  exit /b 1
)

if not exist .venv (
  echo Criando ambiente virtual...
  python -m venv .venv
)
call .venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -q -r requirements.txt

set DATABASE_URL=sqlite:///./estoque.db
start "" cmd /c "timeout /t 5 >nul & start http://localhost:8000"
echo Aplicacao em http://localhost:8000  (feche esta janela para parar)
uvicorn app.main:app --reload
pause
