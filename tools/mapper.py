"""
Professional Component Mapper with visual feedback and robust error handling.
"""
import pyautogui
import json
import time
import os
from typing import Dict, Any, Optional


class ComponentMapper:
    """Advanced component mapping tool with visual feedback."""
    
    def __init__(self):
        self.mapping_file = "mapped_components.json"
        self.components = self._load_existing_mappings()
        self.wholescreen_added = False
        
        print("🎯 Component Mapper Professional")
        print("=" * 50)
    
    def _load_existing_mappings(self) -> Dict[str, Any]:
        """Load existing mappings with error handling."""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    components = json.load(f)
                print(f"✅ Loaded {len(components)} existing components")
                return components
            else:
                print("📝 No existing mapping file found. Starting fresh.")
                return {}
        except Exception as e:
            print(f"❌ Error loading mappings: {e}")
            return {}
    
    def _ensure_wholescreen(self):
        """Ensure WHOLESCREEN component exists."""
        if "WHOLESCREEN" not in self.components and not self.wholescreen_added:
            print("\n📺 Setting up WHOLESCREEN boundary...")
            try:
                screen_width, screen_height = pyautogui.size()
                self.components["WHOLESCREEN"] = {
                    "screenBoundaries": {
                        "minX": 0,
                        "minY": 0, 
                        "maxX": screen_width,
                        "maxY": screen_height
                    }
                }
                self.wholescreen_added = True
                print(f"✅ WHOLESCREEN set to: {screen_width}x{screen_height}")
            except Exception as e:
                print(f"❌ Failed to set WHOLESCREEN: {e}")
    
    def _save_mappings(self):
        """Save mappings with error handling."""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.components, f, indent=2)
            print(f"💾 Mappings saved to {self.mapping_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save mappings: {e}")
            return False
    
    def _get_user_input(self, prompt: str) -> Optional[str]:
        """Get user input with interruption handling."""
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            return None
    
    def _record_single_point(self, description: str) -> Optional[tuple]:
        """Record a single screen coordinate."""
        print(f"\n📍 {description}")
        print("   Move mouse to position and press Enter...")
        print("   Press Ctrl+C to cancel")
        
        try:
            input("   Ready? Press Enter...")
            x, y = pyautogui.position()
            print(f"   ✅ Recorded: ({x}, {y})")
            return (x, y)
        except (KeyboardInterrupt, EOFError):
            print("   ❌ Cancelled")
            return None
    
    def _record_boundary(self, component_name: str) -> bool:
        """Record boundary for a component."""
        print(f"\n🎯 Recording: {component_name}")
        print("-" * 40)
        
        # Record top-left corner
        top_left = self._record_single_point("Top-Left corner of the component")
        if top_left is None:
            return False
        
        # Record bottom-right corner  
        bottom_right = self._record_single_point("Bottom-Right corner of the component")
        if bottom_right is None:
            return False
        
        x1, y1 = top_left
        x2, y2 = bottom_right
        
        # Calculate boundaries
        min_x = min(x1, x2)
        min_y = min(y1, y2)
        max_x = max(x1, x2)
        max_y = max(y2, y2)
        
        print(f"\n📐 Boundary calculated:")
        print(f"   Top-Left: ({min_x}, {min_y})")
        print(f"   Bottom-Right: ({max_x}, {max_y})")
        print(f"   Width: {max_x - min_x}px, Height: {max_y - min_y}px")
        
        # Confirm with user
        confirm = self._get_user_input("\n✅ Keep this boundary? (y/n): ")
        if confirm and confirm.lower().startswith('y'):
            self.components[component_name] = {
                "screenBoundaries": {
                    "minX": min_x,
                    "minY": min_y,
                    "maxX": max_x,
                    "maxY": max_y
                }
            }
            print(f"✅ Component '{component_name}' mapped successfully!")
            return True
        else:
            print("❌ Mapping discarded")
            return False
    
    def record_component(self):
        """Record a new component with full workflow."""
        print("\n" + "=" * 50)
        print("🆕 New Component Mapping")
        print("=" * 50)
        
        # Get component name
        component_name = self._get_user_input("\nEnter component name: ")
        if not component_name:
            return
        
        component_name = component_name.strip()
        if not component_name:
            print("❌ Component name cannot be empty!")
            return
        
        if component_name in self.components:
            overwrite = self._get_user_input(f"⚠️  Component '{component_name}' already exists. Overwrite? (y/n): ")
            if not overwrite or not overwrite.lower().startswith('y'):
                print("❌ Mapping cancelled")
                return
        
        # Record boundary
        if self._record_boundary(component_name):
            self._save_mappings()
    
    def record_chrome_tab(self, tab_number: int):
        """Specialized method for recording Chrome tabs."""
        component_name = f"chrometab{tab_number}"
        
        print(f"\n🌐 Recording Chrome Tab {tab_number}")
        print("=" * 40)
        print("Instructions:")
        print("1. Make sure Chrome is visible")
        print("2. Hover over the TAB (not the content area)")
        print("3. We'll record the clickable tab area")
        
        if self._record_boundary(component_name):
            self._save_mappings()
    
    def list_components(self):
        """List all mapped components with details."""
        if not self.components:
            print("\n📭 No components mapped yet!")
            return
        
        print(f"\n📋 Mapped Components ({len(self.components)} total)")
        print("=" * 60)
        
        for name, data in sorted(self.components.items()):
            bounds = data.get('screenBoundaries', {})
            min_x = bounds.get('minX', 0)
            min_y = bounds.get('minY', 0)
            max_x = bounds.get('maxX', 0)
            max_y = bounds.get('maxY', 0)
            
            width = max_x - min_x
            height = max_y - min_y
            
            print(f"🔹 {name:20} | Pos: ({min_x:4},{min_y:4}) | Size: {width:4}x{height:4}")
    
    def delete_component(self):
        """Delete a component."""
        if not self.components:
            print("\n📭 No components to delete!")
            return
        
        self.list_components()
        component_name = self._get_user_input("\nEnter component name to delete: ")
        
        if component_name and component_name in self.components:
            confirm = self._get_user_input(f"🗑️  Delete '{component_name}'? (y/n): ")
            if confirm and confirm.lower().startswith('y'):
                del self.components[component_name]
                self._save_mappings()
                print(f"✅ Component '{component_name}' deleted")
            else:
                print("❌ Deletion cancelled")
        else:
            print("❌ Component not found")
    
    def test_component(self):
        """Test a component by clicking on it."""
        if not self.components:
            print("\n📭 No components to test!")
            return
        
        self.list_components()
        component_name = self._get_user_input("\nEnter component name to test: ")
        
        if component_name and component_name in self.components:
            bounds = self.components[component_name].get('screenBoundaries', {})
            min_x = bounds.get('minX', 0)
            min_y = bounds.get('minY', 0)
            max_x = bounds.get('maxX', 0)
            max_y = bounds.get('maxY', 0)
            
            # Calculate center point
            center_x = (min_x + max_x) // 2
            center_y = (min_y + max_y) // 2
            
            print(f"\n🧪 Testing component: {component_name}")
            print(f"   Moving to: ({center_x}, {center_y})")
            print("   Click will occur in 3 seconds...")
            
            try:
                for i in range(3, 0, -1):
                    print(f"   {i}...")
                    time.sleep(1)
                
                pyautogui.moveTo(center_x, center_y, duration=0.5)
                pyautogui.click()
                print("   ✅ Click executed!")
                
            except KeyboardInterrupt:
                print("   ❌ Test cancelled")
        else:
            print("❌ Component not found")
    
    def show_statistics(self):
        """Show mapping statistics."""
        if not self.components:
            print("\n📊 No components mapped yet!")
            return
        
        chrome_tabs = [name for name in self.components.keys() if 'chrometab' in name.lower()]
        other_components = [name for name in self.components.keys() if 'chrometab' not in name.lower()]
        
        print(f"\n📊 Mapping Statistics")
        print("=" * 40)
        print(f"📦 Total Components: {len(self.components)}")
        print(f"🌐 Chrome Tabs: {len(chrome_tabs)}")
        print(f"🔧 Other Components: {len(other_components)}")
        
        if chrome_tabs:
            print(f"\n🌐 Chrome Tabs: {', '.join(sorted(chrome_tabs))}")
        
        if other_components:
            print(f"🔧 Other Components: {', '.join(sorted(other_components))}")
    
    def run(self):
        """Main application loop."""
        self._ensure_wholescreen()
        
        while True:
            print("\n" + "=" * 50)
            print("🤖 Component Mapper Professional")
            print("=" * 50)
            print("1. 🆕 Record New Component")
            print("2. 🌐 Record Chrome Tab")
            print("3. 📋 List All Components") 
            print("4. 🧪 Test Component")
            print("5. 🗑️  Delete Component")
            print("6. 📊 Show Statistics")
            print("7. 💾 Save Mappings")
            print("8. 🚪 Exit")
            print("-" * 50)
            
            choice = self._get_user_input("Select option (1-8): ")
            
            if choice == "1":
                self.record_component()
            elif choice == "2":
                try:
                    tab_num = int(self._get_user_input("Enter Chrome tab number: ") or "1")
                    self.record_chrome_tab(tab_num)
                except ValueError:
                    print("❌ Please enter a valid number")
            elif choice == "3":
                self.list_components()
            elif choice == "4":
                self.test_component()
            elif choice == "5":
                self.delete_component()
            elif choice == "6":
                self.show_statistics()
            elif choice == "7":
                if self._save_mappings():
                    print("✅ Save successful!")
            elif choice == "8":
                print("\n👋 Thank you for using Component Mapper!")
                break
            else:
                print("❌ Invalid choice. Please try again.")


def main():
    """Main entry point."""
    try:
        mapper = ComponentMapper()
        mapper.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Mapper stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    main()