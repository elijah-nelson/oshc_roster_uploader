setlocal enabledelayedexpansion

:: if .venv directory doesn't exist, create venv
set "found_venv=0"
for /f "delims=" %%a in ('dir /b /AD') do (
    echo %%a | findstr /i ".venv" >nul
    if not errorlevel 1 (
        set "found_venv=1"
        goto :break_loop1
    )
)
:break_loop1
if %found_venv%=="0" (
    python -m venv .venv
)

git pull
:: always update virtual environment since the script isn't ran very often
.\.venv\Scripts\pip.exe install --upgrade -r requirements.txt

:: run main.py
.\.venv\Scripts\python.exe main.py
pause