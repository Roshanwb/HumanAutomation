import pyautogui
import time
import random
import json
import threading
import os
from datetime import datetime
from pynput import keyboard

# File paths
MAPPED_COMPONENTS_FILE = "mapped_components.json"
LOG_DIR = "logs"

# Create logs directory if not exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log file setup
log_file_name = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Global stop flag
stop_flag = False

def log_action(action):
    with open(log_file_name, "a") as log_file:
        log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action}\n")
    print(action)

# Load components from file
def load_mapped_components():
    if not os.path.exists(MAPPED_COMPONENTS_FILE):
        raise FileNotFoundError(f"Mapping file '{MAPPED_COMPONENTS_FILE}' not found.")
    with open(MAPPED_COMPONENTS_FILE, "r") as file:
        return json.load(file)

# Random delay helper
def random_delay(min_ms, max_ms):
    delay = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
    time.sleep(delay)
    log_action(f"Waited for {delay:.2f} seconds")

# Human-like mouse movement with randomized speed
def human_move_to(target_x, target_y):
    import math

    # Current mouse position
    start_x, start_y = pyautogui.position()

    # Randomized speed parameters
    steps = random.randint(10, 20)
    speed_factor = random.uniform(0.005, 0.02)

    # Control points for the Bezier curve
    control_x1 = start_x + random.randint(-50, 50)
    control_y1 = start_y + random.randint(-50, 50)
    control_x2 = target_x + random.randint(-50, 50)
    control_y2 = target_y + random.randint(-50, 50)

    for i in range(steps + 1):
        # Parameter t goes from 0 to 1
        t = i / steps

        # Bezier curve formula
        x = (1 - t) ** 3 * start_x + 3 * (1 - t) ** 2 * t * control_x1 + 3 * (1 - t) * t ** 2 * control_x2 + t ** 3 * target_x
        y = (1 - t) ** 3 * start_y + 3 * (1 - t) ** 2 * t * control_y1 + 3 * (1 - t) * t ** 2 * control_y2 + t ** 3 * target_y

        # Move the mouse to the calculated point
        pyautogui.moveTo(x, y, duration=speed_factor)

    # Final adjustment to ensure the mouse is exactly on the target
    pyautogui.moveTo(target_x, target_y, duration=0.01)
    log_action(f"Moved mouse to ({target_x}, {target_y}) smoothly")

# Random mouse movement
def random_mouse_move():
    screen_width, screen_height = pyautogui.size()
    random_x = random.randint(0, screen_width)
    random_y = random.randint(0, screen_height)
    human_move_to(random_x, random_y)
    log_action(f"Random mouse move to ({random_x}, {random_y})")

# Click component
def click_component(component_id):
    components = load_mapped_components()

    # Normalize keys to lowercase for case-insensitive matching
    components = {key.lower(): value for key, value in components.items()}
    component_id = component_id.lower()

    if component_id not in components:
        log_action(f"Error: Component '{component_id}' not found in mapping. Skipping.")
        return

    component = components[component_id]
    x = random.randint(component['screenBoundaries']['minX'], component['screenBoundaries']['maxX'])
    y = random.randint(component['screenBoundaries']['minY'], component['screenBoundaries']['maxY'])

    human_move_to(x, y)
    pyautogui.click()
    log_action(f"Clicked on component '{component_id}' at ({x}, {y})")

# Type text like a human
def type_text(text, min_delay, max_delay):
    for char in text:
        pyautogui.typewrite(char)
        random_delay(min_delay, max_delay)
    log_action(f"Typed text: '{text}'")

# Press a key
def press_key(key, min_delay, max_delay):
    pyautogui.press(key)
    random_delay(min_delay, max_delay)
    log_action(f"Pressed key: '{key}'")

# Wait command
def wait_command(min_minutes, max_minutes):
    wait_time = random.uniform(min_minutes * 60, max_minutes * 60)
    time.sleep(wait_time)
    log_action(f"Waited for {wait_time / 60:.2f} minutes")

# Execute scenario
def execute_scenario(scenario_file):
    global stop_flag

    with open(scenario_file, "r") as file:
        lines = file.readlines()

    while not stop_flag:
        for line in lines:
            if stop_flag:
                break

            line = line.strip()
            
            # Skip comments or empty lines
            if not line or line.startswith("#"):
                continue

            parts = line.split(",")
            command = parts[0].strip().lower()

            if command.startswith("click"):
                component_id = command.split()[1]
                min_delay, max_delay = map(int, parts[1].strip().split("-"))
                click_component(component_id)
                random_delay(min_delay, max_delay)

            elif command.startswith("movemouse"):
                random_mouse_move()

            elif command.startswith("type"):
                text = command.split("\"", 2)[1]
                min_delay, max_delay = map(int, parts[1].strip().split("-"))
                type_text(text, min_delay, max_delay)

            elif command.startswith("press"):
                key = command.split()[1]
                min_delay, max_delay = map(int, parts[1].strip().split("-"))
                press_key(key, min_delay, max_delay)

            elif command.startswith("wait"):
                min_minutes, max_minutes = map(float, parts[1].strip().split("-"))
                wait_command(min_minutes, max_minutes)

            elif command.startswith("repeat"):
                log_action("Repeating scenario")
                break

        else:
            log_action("Scenario completed. Exiting.")
            break

# Stop automation with keyboard combination
def stop_on_keypress():
    def on_press(key):
        global stop_flag
        if key == keyboard.Key.f4 and keyboard.Controller().pressed(keyboard.Key.ctrl):
            stop_flag = True
            print("Stop command received. Exiting.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Background thread to execute scenario
def run_in_background(scenario_file):
    def run():
        try:
            execute_scenario(scenario_file)
        except Exception as e:
            log_action(f"Error: {e}")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

if __name__ == "__main__":
    scenario_file = "scenario_GLOBAL.txt"
    if not os.path.exists(scenario_file):
        print(f"Scenario file '{scenario_file}' not found.")
    else:
        run_in_background(scenario_file)
        stop_on_keypress()
