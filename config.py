"""
Simple configuration management that's easy to understand.
"""
import json
import os
from typing import Dict, Any


class Config:
    """
    Simple configuration class that holds all our settings.
    """
    
    def __init__(self):
        # Default values - these are our fallback settings
        self.main_scenario_file = "scenarios/main.txt"
        self.log_dir = "logs"
        self.mapped_components_file = "mapped_components.json"
        self.wholescreen_key = "WHOLESCREEN"
        self.special_login_file = "special_login.txt"
        
        # Scenario folders organized by purpose
        self.scenario_folders = {
            "mustdo": "scenarios/mustdo",
            "randos": "scenarios/randos", 
            "fillers": "scenarios/fillers"
        }
        
        # Screen adjustments
        self.delta_x = 0
        self.delta_y = 0
        
        # Behavior settings
        self.default_delay = "500-1500"
    
    def load_from_file(self, config_file: str = "config.json") -> bool:
        """
        Load configuration from a JSON file.
        Returns True if successful, False otherwise.
        """
        try:
            if not os.path.exists(config_file):
                print(f"⚠️  Config file {config_file} not found. Using defaults.")
                return False
            
            with open(config_file, 'r') as file:
                content = file.read()
            
            # Try to parse JSON
            data = json.loads(content)
            
            # Update our settings with values from the file
            self.main_scenario_file = data.get("MAIN_SCENARIO_FILE", self.main_scenario_file)
            self.log_dir = data.get("LOG_DIR", self.log_dir)
            self.mapped_components_file = data.get("MAPPED_COMPONENTS_FILE", self.mapped_components_file)
            self.wholescreen_key = data.get("WHOLESCREEN_KEY", self.wholescreen_key)
            self.special_login_file = data.get("SPECIAL_LOGIN_FILE", self.special_login_file)
            self.scenario_folders = data.get("SCENARIO_FOLDERS", self.scenario_folders)
            self.delta_x = data.get("DeltaX", self.delta_x)
            self.delta_y = data.get("DeltaY", self.delta_y)
            
            print("✅ Configuration loaded successfully!")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON syntax error in config file: {e}")
            print("💡 Check for trailing commas or missing quotes in config.json")
            return False
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False
    
    def ensure_directories(self):
        """Make sure all needed folders exist."""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            for folder in self.scenario_folders.values():
                os.makedirs(folder, exist_ok=True)
            print("✅ All directories ready!")
        except Exception as e:
            print(f"❌ Error creating directories: {e}")


# Create a global config instance
app_config = Config()

# Try to load config, but continue with defaults if it fails
if not app_config.load_from_file():
    print("🔄 Continuing with default configuration...")

app_config.ensure_directories()