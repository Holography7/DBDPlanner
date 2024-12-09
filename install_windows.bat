@echo off
setlocal EnableDelayedExpansion

SET param=
SET version_python=

FOR %%I in (%*) do (
    IF "!param!" == "" (
        SET "param=%%I"
    ) ELSE  IF "!param!" == "--python-version" (
        SET "version_python=%%I"
        IF NOT "!version_python!" == "3.12" (
            IF NOT "!version_python!" == "3.13" (
                ECHO [91mInvalid argument value of python-version: supported only 3.12 and 3.13 versions.[0m
                PAUSE
                EXIT /b 1
            )
        )
        SET param=
    )
)

IF "!version_python!" == "" (
    WHERE python
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [91mPython not installed or not added to PATH.[0m
        ECHO [91mTo install it, Visit https://www.python.org/downloads/ to download it with selected checkbox "Add python.exe to PATH".[0m
        ECHO [91mTo add to PATH, press Win+R, type "SystemPropertiesAdvanced", press "Environment Variables", double-click on "Path" in user environments, press "New" and type "C:\Users\<YOUR_USER>\AppData\Local\Programs\Python\Python312".[0m
        PAUSE
        EXIT /b 1
    )
    FOR /F %%I IN ('python -c "import sys; major, minor = sys.version_info[0:2]; print(f'{major}.{minor}')"') DO SET "version_python=%%I"
    SET python_version_is_correct=
    FOR /F %%I IN ('python -c "import sys; major, minor = sys.version_info[0:2]; print(major == 3 and minor >= 12)"') DO SET "python_version_is_correct=%%I"
    IF "%python_version_is_correct%" == "False" (
        ECHO [91mPython %version_python% is outdated for this project.[0m
        ECHO [91mVisit https://www.python.org/downloads/ to download it with selected checkbox "Add python.exe to PATH".[0m
        PAUSE
        EXIT /b 1
    )
    SET "python_command=python"
) ELSE (
    SET version_codename=%version_python:.=%
    SET "python_command=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python!version_codename!\python.exe"
    IF EXIST "!python_command!" (
        ECHO [92mSelected python version !version_python![0m
    ) ELSE (
        ECHO [91mPython !version_python! not found, using default path ^(!python_command!^)[0m
        PAUSE
        EXIT /b 1
    )
)
IF EXIST .venv\ (
    ECHO [92mVirtual environment already exists.[0m
    FOR /F %%I IN ('.venv\Scripts\python.exe -c "import sys; major, minor = sys.version_info[0:2]; print(f'{major}.{minor}')"') DO SET "venv_version_python=%%I"
    IF "!venv_version_python!" == "!version_python!" (
        ECHO [92mPython version in virtual environment same with selected.[0m
        PAUSE
        EXIT /b 1
    ) ELSE (
        ECHO [91mPython version in virtual environment not same with selected version ^(!venv_version_python! not same with !version_python!^).[0m
        ECHO [91mDelete .venv directory and try again.[0m
        PAUSE
        EXIT /b 1
    )
) ELSE (
    ECHO [93mVirtual environment not exists. Creating...[0m
    START /B /wait !python_command! -m venv .venv
)
ECHO Activating virtual environment...
call .venv\Scripts\activate.bat
ECHO Installing uv...
START /B /wait pip install uv
ECHO Installing other requirements...
START /B /wait uv pip install -r requirements.txt
ECHO [92mInstallation complete![0m
PAUSE
