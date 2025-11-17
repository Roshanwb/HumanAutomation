@echo off
title Dependency Checker
color 0e

:: Set the current directory to the script directory
cd /d "%~dp0"

echo.
echo ==============================
echo    Dependency Checker
echo ==============================
echo.

echo Checking required packages...
echo.

set all_good=1

:: Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i
) else (
    echo ❌ Python not found
    set all_good=0
)

:: Check packages
for %%p in (pyautogui pynput tkinter) do (
    python -c "import %%p" >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ %%p
    ) else (
        echo ❌ %%p
        set all_good=0
    )
)

echo.
if %all_good% equ 1 (
    echo ==============================
    echo    ALL DEPENDENCIES OK!
    echo ==============================
    echo.
    echo You're ready to run HumanAutomation.
) else (
    echo ==============================
    echo    MISSING DEPENDENCIES
    echo ==============================
    echo.
    echo Run installer.bat to fix missing dependencies.
)

echo.
pause