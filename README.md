# HumanAutomation Professional 🤖

A professional, user-friendly automation framework for creating human-like interactions with your computer. Perfect for automation, testing, and workflow optimization.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Quick Start

### For End Users:
1. **Download** the latest release
2. **Run** `start.bat` (Windows) or `launcher.bat`
3. **Follow** the on-screen instructions

### For Developers:
```bash
# Clone the repository
git clone https://github.com/Roshanwb/humanautomation.git
cd humanautomation

# Run setup (Windows)
setup_project.bat

# Install dependencies
installer.bat

# Launch application
launcher.bat
```

## 📁 Project Structure

```
HumanAutomation/
├── main.py              # Main application entry point
├── core/                # Core automation engine
│   ├── application.py   # Main application logic
│   ├── commands.py      # Command pattern implementation
│   ├── events.py        # Event system
│   └── scenario_parser.py # Scenario file parser
├── gui/                 # User interface
│   └── main_window.py   # Modern GUI interface
├── tools/               # Helper tools
│   ├── scenario_maker.py # Visual scenario creator
│   ├── mapper.py        # Component mapping tool
│   └── mapper_gui.py    # GUI mapper adjuster
├── scenarios/           # Scenario definitions
│   ├── mustdo/          # Essential scenarios
│   ├── randos/          # Random scenarios (50% chance)
│   └── fillers/         # Filler activities
├── logs/                # Execution logs
└── docs/                # Documentation
```

## 🛠️ Installation

### Prerequisites
- **Python 3.8 or higher**
- **Windows, macOS, or Linux**

### Automated Installation (Recommended)
```bash
# Windows
installer.bat
```
```bash
# Linux/macOS
chmod +x installer.sh
./installer.sh
```

### Manual Installation
```bash
# Install Python dependencies
pip install pyautogui pynput

# Verify installation
python -c "import pyautogui, tkinter; print('Dependencies installed successfully!')"
```

## 🎯 Features

### ✨ Core Capabilities
- **Human-like Interactions**: Realistic mouse movements and typing
- **Scenario System**: Define automation sequences in simple text files
- **Component Mapping**: Visual tool to map screen elements
- **Modern GUI**: Professional interface with real-time monitoring
- **Event System**: Decoupled communication between components

### 🎮 Command Types
- `click component_name` - Click on mapped components
- `type "text here"` - Type text with human-like delays  
- `wait 1-5` - Wait for random time (minutes)
- `movemouse` - Random mouse movement
- `beep` - Audio feedback
- `call scenario_name` - Execute other scenarios

### 🛡️ Safety Features
- **Pause/Resume**: Stop automation at any time
- **Emergency Stop**: Immediate halt of all activities
- **Boundary Checking**: Prevents accidental off-screen actions
- **State Saving**: Resume from where you left off

## 📖 Usage Guide

### 1. First Time Setup
```bash
# Run the setup script
setup_project.bat

# This creates:
# - Directory structure
# - Default config.json
# - Sample scenarios
```

### 2. Map Your Components
```bash
# Launch the mapper tool
launcher.bat -> "Component Mapper"

# Or directly:
python tools/mapper.py
```

### 3. Create Scenarios
```bash
# Use the visual scenario maker
launcher.bat -> "Scenario Maker"

# Or edit text files in scenarios/ folder
```

### 4. Run Automation
```bash
# Start the main application
launcher.bat -> "Run Main Application"

# Or run directly:
python main.py
```

## 📝 Example Scenario

Create `scenarios/demo.txt`:
```txt
# Simple demo scenario
movemouse
wait, 0.1-0.3
click login_button, 500-1500
type "username@example.com", 100-300
click password_field, 500-1000
type "securepassword123", 100-300
click submit_button, 1000-2000
wait, 2-5
beep, 500-1000
```

## 🎪 Batch Files Overview

| File | Purpose | Usage |
|------|---------|-------|
| `launcher.bat` | Main menu | Primary launcher |
| `start.bat` | Quick start | One-click launch |
| `installer.bat` | Dependency setup | First-time installation |
| `setup_project.bat` | Project setup | Initialize folder structure |
| `check_deps.bat` | Dependency check | Verify installation |
| `dev_run.bat` | Development mode | Run with debug output |
| `clean_logs.bat` | Maintenance | Clean up log files |

## 🔧 Configuration

Edit `config.json` to customize behavior:
```json
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
```

## 🐛 Troubleshooting

### Common Issues

**"Python not found"**
- Install Python from [python.org](https://python.org)
- Check "Add Python to PATH" during installation

**"tkinter not available"**
- **Windows**: Reinstall Python, select "tcl/tk and IDLE"
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: Usually pre-installed

**"Import errors"**
```bash
# Reinstall dependencies
pip install --force-reinstall pyautogui pynput
```

**"Permission errors"**
- Run as administrator (Windows)
- Use `sudo` (Linux/macOS)

### Getting Help
1. Check `logs/` folder for error details
2. Run `check_deps.bat` to verify installation
3. Create an issue on GitHub with:
   - Error message
   - Your OS and Python version
   - Steps to reproduce

## 🚀 Advanced Usage

### Creating Custom Commands
```python
# In core/commands.py
class CustomCommand(Command):
    def execute(self, params):
        print("Custom command executed!")
        # Add your custom logic here

# Register the command
CommandFactory.register_command('custom', CustomCommand)
```

### Event System
```python
from core.events import event_bus

def my_handler(data):
    print(f"Event received: {data}")

# Subscribe to events
event_bus.subscribe("automation_started", my_handler)
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup
```bash
# Clone and setup
git clone https://github.com/Roshanwb/humanautomation.git
cd humanautomation
setup_project.bat
installer.bat

# Run in development mode
dev_run.bat
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern software architecture principles
- Clean codebase designed for learning and extension
- Professional-grade error handling and logging
- Cross-platform compatibility

---

**Happy Automating!** 🎉

For support, questions, or suggestions:
- 📧 Email: roshanwb@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/Roshanwb/humanautomation/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Roshanwb/humanautomation/discussions)

---

<div align="center">

*If this project helped you, please give it a ⭐!*

</div>
