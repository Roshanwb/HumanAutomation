@echo off
title HumanAutomation - Quick Start
color 17

:: Set the current directory to the script directory
cd /d "%~dp0"

echo.
echo ==============================
echo    HumanAutomation Quick Start
echo ==============================
echo.

:: Check if dependencies are installed
python -c "import pyautogui, tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Required packages not found.
    echo.
    echo Running installer...
    timeout /t 2 >nul
    call installer.bat
    if %errorlevel% neq 0 (
        pause
        exit /b 1
    )
)

echo ✅ Dependencies verified
echo.
echo Starting main application...
timeout /t 2 >nul

:: Run the main application
python main.py

:: If main.py fails, show error
if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to start main application.
    echo Error code: %errorlevel%
    echo.
    echo Try running the installer first.
    pause
)