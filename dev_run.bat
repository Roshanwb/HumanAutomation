@echo off
title HumanAutomation - Development Mode
color 27

:: Set the current directory to the script directory
cd /d "%~dp0"

echo.
echo ==============================
echo    Development Mode
echo ==============================
echo.
echo This will run the automation with console output
echo and debug information enabled.
echo.
echo Press Ctrl+C to stop execution.
echo.

:: Set environment variable for development mode
set HUMAN_AUTOMATION_DEV=1

:: Run the core automation
python core/run.py

:: Reset environment variable
set HUMAN_AUTOMATION_DEV=