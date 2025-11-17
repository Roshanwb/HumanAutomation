"""
Simple configuration management that's easy to understand.
We'll use Python classes instead of JSON for better type safety.
"""
import json
import os
from typing import Dict, Any


class Config:
    """
    Simple configuration class that holds all our settings.
    Think of this as a central place for all your app's settings.
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
            "mustdo": "scenarios/mustdo",    # Must-run scenarios
            "randos": "scenarios/randos",    # Random scenarios (50% chance)
            "fillers": "scenarios/fillers",  # Filler activities
        }
        
        # Screen adjustments
        self.delta_x = 0
        self.delta_y = 0
        
        # Behavior settings
        self.default_delay = "500-1500"  # Default click delays
    
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
                data = json.load(file)
            
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
            
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False
    
    def ensure_directories(self):
        """Make sure all needed folders exist."""
        os.makedirs(self.log_dir, exist_ok=True)
        for folder in self.scenario_folders.values():
            os.makedirs(folder, exist_ok=True)
        print("✅ All directories ready!")


# Create a global config instance that we can use everywhere
app_config = Config()