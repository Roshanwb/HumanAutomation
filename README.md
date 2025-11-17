HumanAutomation Professional 🤖
A professional, human-like automation framework for GUI automation with clean architecture and easy extensibility.

https://img.shields.io/badge/Python-3.8+-blue.svg
https://img.shields.io/badge/Platform-Windows%2520%257C%2520Linux%2520%257C%2520macOS-lightgrey.svg
https://img.shields.io/badge/License-MIT-green.svg

🚀 Quick Start
Option 1: One-Click Install (Windows)
Download the latest release

Run start.bat

Follow the installation prompts

Option 2: Manual Setup
bash
# Clone the repository
git clone https://github.com/yourusername/humanautomation.git
cd humanautomation

# Run the installer
./installer.bat  # Windows
# or
python installer.py  # Cross-platform
📋 What is HumanAutomation?
HumanAutomation is a sophisticated automation framework that:

Mimics human behavior with realistic mouse movements and typing

Uses visual components instead of fragile screen coordinates

Supports complex scenarios with conditional logic and randomness

Provides professional tools for creating and managing automations

🛠️ Features
Core Features
✅ Human-like mouse movements and typing

✅ Visual component mapping (click areas, not coordinates)

✅ Scenario-based automation

✅ Real-time control (pause, resume, stop)

✅ Professional GUI interface

✅ Cross-platform support

Professional Tools
Scenario Maker - Visual scenario creation

Component Mapper - Define clickable areas

Mapper Adjuster - Fine-tune component positions

Log Viewer - Real-time execution monitoring

📁 Project Structure
text
HumanAutomation/
├── 📄 main.py                 # Main application entry point
├── 📄 launcher.bat            # Main launcher (Windows)
├── 📄 installer.bat           # Dependency installer
├── 📄 start.bat               # Quick start script
├── 📄 config.json             # Application configuration
├── 📁 core/                   # Core automation engine
│   ├── 📄 application.py      # Main application logic
│   ├── 📄 commands.py         # Automation commands
│   ├── 📄 scenario_parser.py  # Scenario file parser
│   └── 📄 events.py           # Event system
├── 📁 gui/                    # User interface
│   └── 📄 main_window.py      # Main control panel
├── 📁 tools/                  # Utility tools
│   ├── 📄 scenario_maker.py   # Scenario creation tool
│   ├── 📄 mapper.py           # Component mapping tool
│   └── 📄 mapper_gui.py       # Visual mapper adjuster
├── 📁 scenarios/              # Automation scenarios
│   ├── 📁 mustdo/             # Essential scenarios
│   ├── 📁 randos/             # Random scenarios (50% chance)
│   └── 📁 fillers/            # Filler activities
└── 📁 logs/                   # Execution logs
🎯 How It Works
1. Map Your Components
Use the Component Mapper to define clickable areas on your screen:

bash
# Run the mapper tool
python tools/mapper.py
2. Create Scenarios
Build automation sequences using the Scenario Maker or text files:

Example Scenario (scenarios/main.txt):

txt
# Main automation scenario
movemouse                    # Random mouse movement
click login_button, 500-1500 # Click with random delay
type "username", 100-300     # Type like a human
wait, 1-3                    # Wait 1-3 seconds
3. Run Automation
Execute your scenarios with the main application:

bash
# Run with GUI
python main.py

# Or run in console mode
python core/run.py
🎮 Usage Guide
Using the Launcher (Recommended)
Run launcher.bat to access all tools through a convenient menu:

text
HumanAutomation Professional
==============================
1. Run Main Application (GUI)
2. Install Dependencies
3. Scenario Maker
4. Component Mapper
5. Mapper Adjuster
6. Run Automation (Console)
7. Open Project Folder
0. Exit
Available Commands
Command	Example	Description
click	click button1, 500-1500	Click a mapped component
type	type "Hello World", 100-300	Type text with delays
wait	wait, 1-5	Wait 1-5 minutes
movemouse	movemouse	Random mouse movement
beep	beep, 200-500	Make a sound
call	call sub_scenario	Run another scenario
Configuration
Edit config.json to customize behavior:

json
{
  "MAIN_SCENARIO_FILE": "scenarios/main.txt",
  "LOG_DIR": "logs",
  "SCENARIO_FOLDERS": {
    "mustdo": "scenarios/mustdo",
    "randos": "scenarios/randos",
    "fillers": "scenarios/fillers"
  },
  "DeltaX": 0,
  "DeltaY": 0
}
🔧 Advanced Features
Special Login Scenario
Automatically runs at specific times (3:01-3:10 AM) for maintenance tasks.

Random Scenarios
Scenarios in the randos folder have a 50% chance of execution.

Filler Activities
Random background activities that make automation seem more human.

Progress Tracking
Real-time progress bars and detailed logging.

🐛 Troubleshooting
Common Issues
"Python not found"

Install Python from python.org

Check "Add Python to PATH" during installation

"tkinter not available"

Windows: Reinstall Python, select "tcl/tk and IDLE"

Linux: sudo apt-get install python3-tk

macOS: Usually pre-installed

"Import errors"

Run installer.bat to install dependencies

Or manually: pip install pyautogui pynput

Log Files
Check the logs/ directory for detailed execution logs and error information.

🤝 Contributing
We welcome contributions! Here's how to help:

Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit your changes: git commit -m 'Add amazing feature'

Push to the branch: git push origin feature/amazing-feature

Open a Pull Request

Development Setup
bash
# Install development dependencies
pip install pylint black pytest

# Run tests
python -m pytest tests/

# Code formatting
black .
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support
📖 Documentation: Check the docs/ folder

🐛 Bug Reports: Create an Issue

💡 Feature Requests: Suggest a Feature

❓ Questions: Discussions

🚀 Quick Commands Reference
bash
# Installation & Setup
./installer.bat                    # Install dependencies
./check_deps.bat                   # Verify installation
./setup_project.bat                # Create project structure

# Running the Application
./launcher.bat                     # Main menu (recommended)
./start.bat                        # Quick start
python main.py                     # GUI application
python core/run.py                 # Console mode

# Tools
python tools/scenario_maker.py     # Create scenarios
python tools/mapper.py             # Map components
python tools/mapper_gui.py         # Adjust mappings

# Maintenance
./clean_logs.bat                   # Clear log files
./dev_run.bat                      # Development mode
Happy Automating! 🎉

If you find this project useful, please give it a ⭐ on GitHub!

HumanAutomation Professional - Making automation feel human 🤖✨

📥 Downloadable Version
Save the following as README.md in your project root:

markdown
# HumanAutomation Professional 🤖

[Content from above...]
This README provides:

✅ Clear installation instructions

✅ Visual hierarchy with emojis

✅ Comprehensive feature overview

✅ Step-by-step usage guide

✅ Troubleshooting section

✅ Professional formatting

✅ Easy to copy and paste

The file is ready to upload to GitHub and will display beautifully with proper formatting and badges!