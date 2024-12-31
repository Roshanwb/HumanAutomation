@echo off
title Automation Program Launcher
color 1f

:menu
cls
echo ==============================
echo    Automation Program Menu
echo ==============================
echo 1. Run Automation
echo 2. Scenario Maker
echo 3. Mapper
echo 4. Exit
echo ==============================
set /p choice="Select an option: "

if "%choice%"=="1" (
    call :run_program "python run.py"
    goto menu
)
if "%choice%"=="2" (
    call :run_program "python scenario_maker.py"
    goto menu
)
if "%choice%"=="3" (
    call :run_program "python mapper.py"
    goto menu
)
if "%choice%"=="4" (
    exit
)

echo Invalid choice, please try again.
pause
goto menu

:run_program
rem Run the given program and prevent batch file termination
cls
echo Running %~1...
echo ==============================
start "" /wait cmd /c %~1
if %errorlevel% NEQ 0 (
    echo Program exited or was interrupted. Returning to the main menu.
)
pause
exit /b
