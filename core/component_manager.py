"""
Manages component mapping and clicking with DeltaX/DeltaY adjustments.
"""
import json
import os
import random
from typing import Dict, Any, Optional
import pyautogui


class ComponentManager:
    """
    Manages screen components with the same logic as original run.py
    Handles DeltaX/DeltaY adjustments and component clicking.
    """
    
    def __init__(self, config):
        self.config = config
        self.mapping_file = config.mapped_components_file
        self.components = {}
        self.last_chrome_tab = None
        self.delta_x = config.delta_x
        self.delta_y = config.delta_y
        self.load_components()
    
    def load_components(self) -> None:
        """Load components from file with DeltaX/DeltaY adjustments."""
        if not os.path.exists(self.mapping_file):
            print(f"❌ Mapping file '{self.mapping_file}' not found.")
            return
        
        with open(self.mapping_file, "r") as file:
            components = json.load(file)
        
        # Apply DeltaX and DeltaY to all components (same as original run.py)
        for component_name, component in components.items():
            if "chrometab" not in component_name.lower(): 
                continue
            if 'screenBoundaries' in component:
                component['screenBoundaries']['minX'] += self.delta_x
                component['screenBoundaries']['maxX'] += self.delta_x
                component['screenBoundaries']['minY'] += self.delta_y
                component['screenBoundaries']['maxY'] += self.delta_y
        
        self.components = components
        print(f"✅ Loaded {len(components)} components with DeltaX={self.delta_x}, DeltaY={self.delta_y}")
    
    def click_component(self, component_id: str) -> bool:
        """Click on a component with the same logic as original run.py."""
        if not self.components:
            print("❌ No components loaded.")
            return False
            
        component_id = component_id.lower()
        components = {key.lower(): value for key, value in self.components.items()}
        
        if component_id not in components:
            print(f"❌ Component '{component_id}' not found in mapping.")
            return False
        
        component = components[component_id]
        
        # Get random position within component boundaries
        x = random.randint(component['screenBoundaries']['minX'], component['screenBoundaries']['maxX'])
        y = random.randint(component['screenBoundaries']['minY'], component['screenBoundaries']['maxY'])
        
        # Human-like movement
        pyautogui.moveTo(x, y, duration=random.uniform(0.5, 1.5))
        pyautogui.click()
        
        print(f"🖱️  Clicked on component '{component_id}' at ({x}, {y})")
        
        # Update last Chrome tab if applicable
        if "chrometab" in component_id:
            self.last_chrome_tab = component
            print(f"📌 Last Chrome tab set to: {component_id}")
        
        return True
    
    def click_last_chrome_tab(self) -> bool:
        """Click the last Chrome tab."""
        if not self.last_chrome_tab:
            print("❌ No last Chrome tab recorded.")
            return False
        
        x = random.randint(self.last_chrome_tab['screenBoundaries']['minX'], 
                          self.last_chrome_tab['screenBoundaries']['maxX'])
        y = random.randint(self.last_chrome_tab['screenBoundaries']['minY'], 
                          self.last_chrome_tab['screenBoundaries']['maxY'])
        
        pyautogui.moveTo(x, y, duration=random.uniform(0.5, 1.5))
        pyautogui.click()
        
        print("🖱️  Clicked on the last Chrome tab.")
        return True
    
    def get_component_position(self, component_id: str) -> Optional[tuple]:
        """Get a random position within a component's boundaries."""
        if not self.components:
            return None
            
        component_id = component_id.lower()
        components = {key.lower(): value for key, value in self.components.items()}
        
        if component_id not in components:
            return None
        
        component = components[component_id]
        x = random.randint(component['screenBoundaries']['minX'], component['screenBoundaries']['maxX'])
        y = random.randint(component['screenBoundaries']['minY'], component['screenBoundaries']['maxY'])
        
        return (x, y)