@echo off
title Clean Log Files
color 0c

:: Set the current directory to the script directory
cd /d "%~dp0"

echo.
echo ==============================
echo    Clean Log Files
echo ==============================
echo.

set /p confirm="This will delete all log files. Continue? (y/N): "

if /i "%confirm%" neq "y" (
    echo Operation cancelled.
    timeout /t 2 >nul
    exit /b 0
)

echo.
echo Deleting log files...
if exist logs\*.txt (
    del /q logs\*.txt
    echo ✅ Log files deleted
) else (
    echo ℹ️  No log files found
)

echo.
echo Cleaning temporary files...
del /q pid.txt 2>nul
del /q program_state.json 2>nul

echo.
echo ✅ Cleanup complete!
timeout /t 2 >nul