setlocal

:: seperate file to main.bat so that any changes to main.bat get loaded before its executed
git pull
.\main.bat
