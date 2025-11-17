"""
Advanced scenario file resolution with folder-specific rules.
"""
import os
import random
from typing import Optional, Dict, List
from config import app_config


   
class ScenarioResolver:
    """
    Resolves scenario names to actual file paths with the same logic as original run.py
    """
    
    def __init__(self, config=None):
        self.config = config or app_config
        self.scenario_folders = self.config.scenario_folders
    
    def find_scenario_file(self, scenario_name: str) -> Optional[str]:
        """
        Find scenario file with the same logic as original run.py:
        - Check all scenario folders
        - For 'randos' folder: 50% chance to execute
        - Return first found file that meets criteria
        """
        found_file = None
        is_randos = False
        
        for folder_key, folder_path in self.scenario_folders.items():
            candidate = os.path.join(folder_path, f"{scenario_name}.txt")
            
            if os.path.exists(candidate):
                if folder_key == "randos":  # Check if it's a `randos` folder
                    is_randos = True
                    should_execute = random.choice([True, False])  # 50% chance
                    
                    if should_execute:
                        print(f"🎲 Executing randos scenario: {scenario_name}")
                        return candidate
                    else:
                        print(f"🎲 Skipping randos scenario: {scenario_name}")
                        continue  # Skip this `randos` file
                else:
                    # Non-randos file found
                    found_file = candidate
        
        # If no `randos` scenario was executed, return the first non-randos file
        if found_file:
            return found_file
        
        print(f"❌ Scenario file for '{scenario_name}' not found.")
        return None
        
    def find_executable_file(self, file_name: str) -> Optional[str]:
        """
        Find executable file with proper path resolution.
        Handles both scripts in scenario folders and dedicated executables folder.
        """
       
        # Then try scenario folders with randos logic
        found_file = None
        is_randos = False
        
        for folder_key, folder_path in self.config.scenario_folders.items():
            candidate = os.path.join(folder_path, f"{file_name}.txt")
            
            if os.path.exists(candidate):
                if folder_key == "randos":  # Check if it's a `randos` folder
                    is_randos = True
                    should_execute = random.choice([True, False])  # 50% chance
                    
                    if should_execute:
                        print(f"🎲 Executing randos executable: {file_name}")
                        return candidate
                    else:
                        print(f"🎲 Skipping randos executable: {file_name}")
                        continue  # Skip this `randos` file
                else:
                    # Non-randos file found
                    found_file = candidate
        
        # If no `randos` executable file was executed, return the first non-randos file
        if found_file:
            return found_file
        
        print(f"❌ Executable file for '{file_name}' not found.")
        return None

    def get_all_scenarios(self, folder_type: str = None) -> List[str]:
        """Get all scenario files in a specific folder type."""
        if folder_type and folder_type in self.scenario_folders:
            folder_path = self.scenario_folders[folder_type]
            if os.path.exists(folder_path):
                return [f[:-4] for f in os.listdir(folder_path) if f.endswith('.txt')]
        return []