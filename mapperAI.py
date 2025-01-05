import pyautogui
from pynput import mouse, keyboard
import json
import time
from datetime import datetime
import os

# Paths
MAPPED_COMPONENTS_FILE = "mapped_components.json"
GEN_DIR = "generated_scenario"
# Globals
recording = False
stop_flag = False

# Create logs directory if not exists
if not os.path.exists(GEN_DIR):
    os.makedirs(GEN_DIR)

OUTPUT_SCENARIO_FILE = os.path.join(GEN_DIR,f"generated_scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Load mapped components
def load_mapped_components():
    """Load mapped components from the JSON file."""
    if not os.path.exists(MAPPED_COMPONENTS_FILE):
        print(f"Error: '{MAPPED_COMPONENTS_FILE}' not found.")
        return {}
    with open(MAPPED_COMPONENTS_FILE, "r") as file:
        return json.load(file)

# Find all components overlapping a click
def find_overlapping_components(x, y, mapped_components):
    """Find all mapped components overlapping with a given click position."""
    overlapping = []
    for component_id, data in mapped_components.items():
        if component_id.upper() in {"WHOLESCREEN", "MINISCREEN"}:  # Ignore irrelevant components
            continue
        bounds = data["screenBoundaries"]
        if bounds["minX"] <= x <= bounds["maxX"] and bounds["minY"] <= y <= bounds["maxY"]:
            overlapping.append(component_id)
    return overlapping

# Process click and write to scenario file
def process_click(x, y, mapped_components, output_file):
    """Process a click and write the appropriate command to the scenario file."""
    overlapping_components = find_overlapping_components(x, y, mapped_components)
    if overlapping_components:
        if len(overlapping_components) == 1:
            component_str = overlapping_components[0]
        else:
            component_str = "/".join(overlapping_components)
    else:
        component_str = f"UNKNOWN({x}, {y})"
    
    with open(output_file, "a") as file:
        file.write(f"Click {component_str}, 500-1500\n")
    print(f"Recorded: Click {component_str}, 500-1500")  # Debug information

# Handle mouse click events
def on_click(x, y, button, pressed):
    """Handle mouse click events."""
    if not pressed or not recording:  # Skip if not recording or mouse released
        return
    print(f"Mouse clicked at ({x}, {y})")  # Debug information
    process_click(x, y, mapped_components, OUTPUT_SCENARIO_FILE)

# Handle keyboard events for stopping
def on_press(key):
    global stop_flag
    if key == keyboard.Key.esc:  # Stop on ESC
        print("ESC pressed. Stopping...")
        stop_flag = True
        return False

# Start recording mouse clicks
def start_recording():
    """Start recording mouse clicks."""
    global recording, stop_flag
    print("Recording started. Press ESC to stop.")
    recording = True
    stop_flag = False

    # Start mouse listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    # Start keyboard listener for stopping
    with keyboard.Listener(on_press=on_press) as listener:
        while not stop_flag:
            time.sleep(0.1)
        recording = False
        mouse_listener.stop()
        print("Recording stopped.")

# Main function
def main():
    global mapped_components
    print("Loading mapped components...")
    mapped_components = load_mapped_components()
    if not mapped_components:
        print("No mapped components found. Exiting.")
        return
    
    print(f"Loaded {len(mapped_components)} mapped components.")
    print(f"Output scenario file: {OUTPUT_SCENARIO_FILE}")
    print("Press ESC to stop recording.")
    start_recording()

if __name__ == "__main__":
    main()
