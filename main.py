"""
HumanAutomation Professional - Main Entry Point
"""
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 50)
    print("🤖 HumanAutomation Professional")
    print("=" * 50)
    
    try:
        # Try to import and run the GUI
        from gui.main_window import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Make sure all required files are present:")
        print("   - gui/main_window.py")
        print("   - core/application.py") 
        print("   - tools/ folder with mapper files")
        print("\nTry running the setup_project.bat first!")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()