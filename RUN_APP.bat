@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto run
where py >nul 2>nul
if errorlevel 1 (
    python -m venv .venv
) else (
    py -3 -m venv .venv
)
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt
if errorlevel 1 goto fail
:run
".venv\Scripts\python.exe" -c "import streamlit, pandas" >nul 2>nul
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt
    if errorlevel 1 goto fail
)
echo Opening Lab 18. Leave this window open while using the app.
".venv\Scripts\python.exe" -m streamlit run app.py --browser.gatherUsageStats false
pause
exit /b
:fail
echo Setup failed. The package or Python-version error is shown above.
if exist ".venv\Scripts\python.exe" ".venv\Scripts\python.exe" --version
echo Copy the exact error above into your AI chat if you need help.
pause
exit /b 1
