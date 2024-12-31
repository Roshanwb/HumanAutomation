import pyautogui
import json
import time

# File to save mappings
MAPPING_FILE = "mapped_components.json"

# Initialize mapping dictionary
mappings = {}

# Load existing mappings if they exist
try:
    with open(MAPPING_FILE, "r") as file:
        mappings = json.load(file)
except FileNotFoundError:
    print("No existing mapping file found. Starting fresh.")

def save_mappings():
    with open(MAPPING_FILE, "w") as file:
        json.dump(mappings, file, indent=4)
    print("Mappings saved!")

def record_component():
    print("Hover over the component and press 'Enter' to record.")
    while True:
        try:
            input("Press 'Enter' when ready...")
            x, y = pyautogui.position()
            print(f"Current position: ({x}, {y})")

            # Component boundaries
            print("Move the mouse to the opposite corner of the boundary and press 'Enter'.")
            input("Press 'Enter' to record the boundary corner...")
            x2, y2 = pyautogui.position()
            print(f"Boundary recorded from ({x}, {y}) to ({x2}, {y2}).")

            # Define the component
            component_id = input("Enter a unique component ID: ").strip()
            mappings[component_id] = {
                "screenBoundaries": {
                    "minX": min(x, x2),
                    "minY": min(y, y2),
                    "maxX": max(x, x2),
                    "maxY": max(y, y2)
                }
            }
            print(f"Component '{component_id}' recorded.")
            save_mappings()

            # Ask to continue
            cont = input("Record another component? (y/n): ").strip().lower()
            if cont != 'y':
                break
        except KeyboardInterrupt:
            print("Exiting mapping tool.")
            break

if __name__ == "__main__":
    print("Component Mapping Tool")
    try:
        record_component()
    except KeyboardInterrupt:
        print("\nMapping stopped. Saving data...")
        save_mappings()
