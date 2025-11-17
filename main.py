#!/usr/bin/env python3
"""
Main entry point for HumanAutomation Professional.
This is where everything starts!
"""
import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function that starts our application."""
    print("=" * 50)
    print("🤖 HumanAutomation Professional")
    print("=" * 50)
    
    try:
        # Import and start the GUI
        from gui.main_window import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install pyautogui tkinter")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()