@echo off
title HumanAutomation Installer
color 0a

:: Set the current directory to the script directory
cd /d "%~dp0"

echo.
echo ==============================
echo    HumanAutomation Installer
echo ==============================
echo.

:: Check if Python is installed
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH.
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo During installation, make sure to:
    echo ✓ Check "Add Python to PATH"
    echo ✓ Install pip package manager
    echo.
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python %python_version% detected

:: Check if tkinter is available (for GUI)
echo [2/4] Checking GUI dependencies...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ tkinter is not available.
    echo.
    echo This usually means:
    echo - On Windows: Reinstall Python and select "tcl/tk and IDLE"
    echo - On Linux: Install python3-tk package
    echo - On macOS: Usually comes pre-installed
    echo.
    pause
    exit /b 1
)
echo ✅ tkinter is available

:: Upgrade pip to latest version
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Could not upgrade pip, but will try to continue...
) else (
    echo ✅ pip upgraded to latest version
)

:: Install required packages
echo [4/4] Installing required packages...
echo.
if exist requirements.txt (
    echo Installing from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Installing core packages...
    pip install pyautogui pynput
)

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to install some packages.
    echo You may need to run this as administrator.
    echo.
    pause
    exit /b 1
)

:: Create necessary directories
echo.
echo Creating project directories...
mkdir logs scenarios mustdo randos fillers >nul 2>&1

:: Verify installation
echo.
echo Verifying installation...
python -c "import pyautogui, pynput, tkinter; print('✅ All imports successful')" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ==============================
    echo    INSTALLATION COMPLETE!
    echo ==============================
    echo.
    echo ✅ Python %python_version%
    echo ✅ tkinter GUI support
    echo ✅ pyautogui automation
    echo ✅ pynput input monitoring
    echo.
    echo You can now run the application!
) else (
    echo.
    echo ❌ Installation verification failed.
    echo Some packages may not be installed correctly.
)

echo.
pause