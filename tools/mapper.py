"""
Simple component mapper for recording screen coordinates.
"""
import pyautogui
import json
import time


class ComponentMapper:
    def __init__(self):
        self.mapping_file = "mapped_components.json"
        self.components = self.load_existing_mappings()
    
    def load_existing_mappings(self):
        """Load existing mappings from file."""
        try:
            with open(self.mapping_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_mappings(self):
        """Save all mappings to file."""
        with open(self.mapping_file, 'w') as f:
            json.dump(self.components, f, indent=2)
        print(f"✅ Mappings saved to {self.mapping_file}")
    
    def record_component(self):
        """Record a new component by getting its screen coordinates."""
        print("\n" + "="*50)
        print("🎯 Component Mapping Tool")
        print("="*50)
        
        try:
            print("\n1. Move your mouse to the TOP-LEFT corner of the component")
            print("   Press Enter when ready...")
            input()
            x1, y1 = pyautogui.position()
            print(f"   📍 Top-left: ({x1}, {y1})")
            
            print("\n2. Move your mouse to the BOTTOM-RIGHT corner of the component") 
            print("   Press Enter when ready...")
            input()
            x2, y2 = pyautogui.position()
            print(f"   📍 Bottom-right: ({x2}, {y2})")
            
            # Calculate boundaries
            min_x = min(x1, x2)
            min_y = min(y1, y2)
            max_x = max(x1, x2)
            max_y = max(y1, y2)
            
            print(f"\n   📐 Boundaries: ({min_x}, {min_y}) to ({max_x}, {max_y})")
            
            # Get component name
            component_name = input("\n3. Enter a name for this component: ").strip()
            
            if not component_name:
                print("❌ Component name cannot be empty!")
                return
            
            # Save the component
            self.components[component_name] = {
                "screenBoundaries": {
                    "minX": min_x,
                    "minY": min_y, 
                    "maxX": max_x,
                    "maxY": max_y
                }
            }
            
            print(f"✅ Component '{component_name}' recorded!")
            self.save_mappings()
            
        except KeyboardInterrupt:
            print("\n⏹️  Mapping cancelled")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def list_components(self):
        """List all mapped components."""
        if not self.components:
            print("📭 No components mapped yet!")
            return
        
        print("\n📋 Mapped Components:")
        print("-" * 30)
        for name, data in self.components.items():
            bounds = data.get('screenBoundaries', {})
            print(f"🔹 {name}: ({bounds.get('minX', 0)},{bounds.get('minY', 0)}) "
                  f"to ({bounds.get('maxX', 0)},{bounds.get('maxY', 0)})")
    
    def run(self):
        """Main mapper loop."""
        while True:
            print("\n" + "="*50)
            print("🤖 Component Mapper")
            print("="*50)
            print("1. Record new component")
            print("2. List all components") 
            print("3. Save and exit")
            print("4. Exit without saving")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self.record_component()
            elif choice == "2":
                self.list_components()
            elif choice == "3":
                self.save_mappings()
                print("👋 Goodbye!")
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    mapper = ComponentMapper()
    mapper.run()