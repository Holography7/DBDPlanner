@echo off
WHERE python
IF %ERRORLEVEL% NEQ 0 (
    ECHO [91mPython not installed or not added to PATH.[0m
    ECHO [91mTo install it, Visit https://www.python.org/downloads/ to download it with selected checkbox "Add python.exe to PATH".[0m
    ECHO [91mTo add to PATH, press Win+R, type "SystemPropertiesAdvanced", press "Environment Variables", double-click on "Path" in user environments, press "New" and type "C:\Users\<YOUR_USER>\AppData\Local\Programs\Python\Python312".[0m
    PAUSE
    EXIT /b 1
)
SET version_python=
FOR /F %%I IN ('python -c "import sys; major, minor = sys.version_info[0:2]; print(f'{major}.{minor}')"') DO SET "version_python=%%I"
SET python_version_is_correct=
FOR /F %%I IN ('python -c "import sys; major, minor = sys.version_info[0:2]; print(major == 3 and minor >= 12)"') DO SET "python_version_is_correct=%%I"
IF "%python_version_is_correct%" == "False" (
    ECHO [91mPython %version_python% is outdated for this project.[0m
    ECHO [91mVisit https://www.python.org/downloads/ to download it with selected checkbox "Add python.exe to PATH".[0m
)
IF EXIST .venv\ (
    ECHO [92mVirtual environment already exists.[0m
) ELSE (
    ECHO [93mVirtual environment not exists. Creating...[0m
    START /B /wait python -m venv .venv
)
ECHO Activating virtual environment...
call .venv\Scripts\activate.bat
ECHO Installing uv...
START /B /wait pip install uv
ECHO Installing other requirements...
START /B /wait uv pip install -r requirements.txt
ECHO [92mInstallation complete![0m
PAUSE
