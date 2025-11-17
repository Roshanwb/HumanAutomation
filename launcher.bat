@echo off
title HumanAutomation Launcher
color 1f

:: Set the current directory to the script directory
cd /d "%~dp0"

:: Display the main menu
:menu
cls
echo.
echo ==============================
echo    HumanAutomation Professional
echo ==============================
echo.
echo 1. Run Main Application (GUI)
echo 2. Install Dependencies
echo 3. Scenario Maker
echo 4. Component Mapper
echo 5. Mapper Adjuster
echo 6. Run Core Automation
echo 7. Open Project Folder
echo 0. Exit
echo.
echo ==============================
set /p choice="Select an option: "

if "%choice%"=="1" (
    call :run_python "main.py"
    goto menu
)
if "%choice%"=="2" (
    call :run_batch "installer.bat"
    goto menu
)
if "%choice%"=="3" (
    call :run_python "tools\scenario_maker.py"
    goto menu
)
if "%choice%"=="4" (
    call :run_python "tools\mapper.py"
    goto menu
)
if "%choice%"=="5" (
    call :run_python "tools\mapper_gui.py"
    goto menu
)
if "%choice%"=="6" (
    call :run_python "core\application.py"
    goto menu
)
if "%choice%"=="7" (
    explorer .
    goto menu
)
if "%choice%"=="0" (
    exit /b 0
)

echo.
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:run_python
echo.
echo Starting %~1...
echo ==============================
if not exist "%~1" (
    echo ❌ File not found: %~1
    echo Please make sure all files are in the correct location.
    pause
    exit /b 1
)
python "%~1"
if %errorlevel% NEQ 0 (
    echo.
    echo Program exited with error code %errorlevel%
    echo Please check the console for details.
)
echo.
pause
exit /b %errorlevel%

:run_batch
echo.
echo Running %~1...
echo ==============================
if not exist "%~1" (
    echo ❌ File not found: %~1
    pause
    exit /b 1
)
call "%~1"
echo.
pause
exit /b %errorlevel%