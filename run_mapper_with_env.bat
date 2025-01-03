@echo off
:: Set up a virtual environment and run the Python program

:: Define environment folder
set VENV_DIR=env

:: Check if the virtual environment exists
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

:: Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

:: Upgrade pip to avoid compatibility issues
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install required packages
echo Installing dependencies...
python -m pip install numpy opencv-python pyautogui

:: Run the program
echo Running the program...
python mapper_gui.py

:: Deactivate the environment after the program exits
echo Deactivating virtual environment...
deactivate

pause
