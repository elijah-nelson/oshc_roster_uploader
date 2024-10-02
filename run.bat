setlocal enabledelayedexpansion

:: if .venv directory doesn't exist, create venv and update virtual environment
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
    .\.venv\Scripts\pip.exe install --upgrade -r requirements.txt
)

:: if git pull updates requirements.txt, update virtual environment
for /f "delims=" %%a in ('git pull') do (
    echo "%%a" | findstr /i "requirements.txt" >nul
    if not errorlevel 1 (
        .\.venv\Scripts\pip.exe install --upgrade -r requirements.txt
        goto :break_loop2
    )
)
:break_loop2

:: run main.py
.\.venv\Scripts\python.exe main.py
pause