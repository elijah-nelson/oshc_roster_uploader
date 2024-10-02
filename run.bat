@REM store list of directories in current directory in %FILES%
FOR /F "tokens=*" %%g IN ('dir /b /AD') do (SET FILES=%%g)
@REM if %FILES% doesn't contains the string .venv, create virtual environment
if x%FILES:.venv=%==x%FILES% python -m venv .venv
@REM store output from git pull in %GIT_PULL%
FOR /F "tokens=*" %%g IN ('git pull') do (SET GIT_PULL=%%g)
@REM if %GIT_PULL% contains the string requirements.txt, update virtual environment
if not x%GIT_PULL:requirements.txt=%==x%GIT_PULL% .\.venv\Scripts\pip.exe install --upgrade -r requirements.txt
.\.venv\Scripts\python.exe main.py
pause