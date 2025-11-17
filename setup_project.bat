@echo off
title Project Setup
color 0b

:: Set the current directory to the script directory
cd /d "%~dp0"

echo.
echo ==============================
echo    Project Structure Setup
echo ==============================
echo.

echo Creating directory structure...
echo.

:: Create main directories
for %%d in (
    "core"
    "gui" 
    "tools"
    "scenarios"
    "scenarios\mustdo"
    "scenarios\randos"
    "scenarios\fillers"
    "logs"
    "backup"
    "docs"
) do (
    if not exist "%%d" (
        mkdir "%%d"
        echo Created: %%d
    ) else (
        echo Exists: %%d
    )
)

:: Create basic files if they don't exist
if not exist "config.json" (
    echo Creating default config.json...
    echo {> config.json
    echo   "MAIN_SCENARIO_FILE": "scenarios/main.txt",>> config.json
    echo   "LOG_DIR": "logs",>> config.json
    echo   "MAPPED_COMPONENTS_FILE": "mapped_components.json",>> config.json
    echo   "WHOLESCREEN_KEY": "WHOLESCREEN",>> config.json
    echo   "SPECIAL_LOGIN_FILE": "special_login.txt",>> config.json
    echo   "SCENARIO_FOLDERS": {>> config.json
    echo     "mustdo": "scenarios/mustdo",>> config.json
    echo     "randos": "scenarios/randos",>> config.json
    echo     "fillers": "scenarios/fillers">> config.json
    echo   },>> config.json
    echo   "DeltaX": 0,>> config.json
    echo   "DeltaY": 0>> config.json
    echo }>> config.json
)

if not exist "requirements.txt" (
    echo Creating requirements.txt...
    echo pyautogui>=0.9.53 > requirements.txt
    echo pynput>=1.7.6 >> requirements.txt
)

if not exist "scenarios\main.txt" (
    echo Creating sample scenario...
    echo # Main Automation Scenario > scenarios\main.txt
    echo # Add your commands here >> scenarios\main.txt
    echo. >> scenarios\main.txt
    echo movemouse >> scenarios\main.txt
    echo wait, 0.1-0.5 >> scenarios\main.txt
)

echo.
echo ==============================
echo    PROJECT SETUP COMPLETE!
echo ==============================
echo.
echo Next steps:
echo 1. Run installer.bat to install dependencies
echo 2. Run launcher.bat to start the application
echo.
pause