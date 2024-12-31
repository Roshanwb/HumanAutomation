import pyautogui
import time
import random
import json
import threading
import os
from datetime import datetime
from pynput import keyboard

# File paths
MAIN_SCENARIO_FILE = "main_scenario.txt"
LOG_DIR = "logs"
MAPPED_COMPONENTS_FILE = "mapped_components.json"
WHOLESCREEN_KEY = "WHOLESCREEN"
SPECIAL_LOGIN_FILE = "special_login.txt"
SCENARIO_FOLDERS = {
    "mustdo": "mustdo",
    "randos": "randos",
    "fillers": "fillers"
}

# Create logs directory if not exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log file setup
log_file_name = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Global variables
stop_flag = False
start_time = None
iteration_time_limit = 0
currently_in_filler = False

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

# Human-like mouse movement
def human_move_to(target_x, target_y):
    start_x, start_y = pyautogui.position()
    steps = random.randint(10, 20)
    speed_factor = random.uniform(0.005, 0.02)
    control_x1 = start_x + random.randint(-50, 50)
    control_y1 = start_y + random.randint(-50, 50)
    control_x2 = target_x + random.randint(-50, 50)
    control_y2 = target_y + random.randint(-50, 50)
    
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**3 * start_x + 3 * (1 - t)**2 * t * control_x1 + 3 * (1 - t) * t**2 * control_x2 + t**3 * target_x
        y = (1 - t)**3 * start_y + 3 * (1 - t)**2 * t * control_y1 + 3 * (1 - t) * t**2 * control_y2 + t**3 * target_y
        pyautogui.moveTo(x, y, duration=speed_factor)

    pyautogui.moveTo(target_x, target_y, duration=0.01)
    log_action(f"Moved mouse to ({target_x}, {target_y}) smoothly")

# Random mouse movement
def random_mouse_move():
    components = load_mapped_components()
    screen = components.get(WHOLESCREEN_KEY)
    if not screen:
        raise ValueError("WHOLESCREEN boundary not defined in mapping.")

    random_x = random.randint(screen['screenBoundaries']['minX'], screen['screenBoundaries']['maxX'])
    random_y = random.randint(screen['screenBoundaries']['minY'], screen['screenBoundaries']['maxY'])
    human_move_to(random_x, random_y)
    log_action(f"Random mouse move to ({random_x}, {random_y})")

# Click component
def click_component(component_id):
    components = load_mapped_components()
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

# Wait command
def wait_command(min_minutes, max_minutes):
    wait_time = random.uniform(min_minutes * 60, max_minutes * 60)
    for remaining in range(int(wait_time), 0, -1):
        mins, secs = divmod(remaining, 60)
        print(f"Waiting: {mins:02}:{secs:02} remaining", end="\r")
        time.sleep(1)
    print("\n")
    log_action(f"Waited for {wait_time / 60:.2f} minutes")

# Check for interruption
def check_interruption():
    components = load_mapped_components()
    screen = components.get(WHOLESCREEN_KEY)
    if not screen:
        raise ValueError("WHOLESCREEN boundary not defined in mapping.")

    current_x, current_y = pyautogui.position()
    if not (screen['screenBoundaries']['minX'] <= current_x <= screen['screenBoundaries']['maxX'] and \
            screen['screenBoundaries']['minY'] <= current_y <= screen['screenBoundaries']['maxY']):
        answer = input("Mouse moved outside WHOLESCREEN. Interrupt program? (y/n): ").strip().lower()
        if answer == 'y':
            global stop_flag
            stop_flag = True

# Execute a scenario file
def execute_scenario(scenario_file):
    global stop_flag, start_time, iteration_time_limit, currently_in_filler

    with open(scenario_file, "r") as file:
        lines = file.readlines()

    for line in lines:
        if stop_flag:
            break

        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split(",")
        command = parts[0].strip().lower()

        if command.startswith("click"):
            component_id = command.split()[1]
            click_component(component_id)
        elif command.startswith("movemouse"):
            random_mouse_move()
        elif command.startswith("wait"):
            min_time, max_time = map(float, parts[1].strip().split("-"))
            wait_command(min_time, max_time)
        elif command.startswith("totaltime"):
            min_time, max_time = map(int, parts[1].strip().split("-"))
            iteration_time_limit = random.randint(min_time, max_time) * 60
            start_time = time.time()
            log_action(f"Total time for this iteration: {iteration_time_limit / 60:.2f} minutes")
        elif command.startswith("repeat"):
            elapsed_time = time.time() - start_time
            remaining_time = max(0, iteration_time_limit - elapsed_time)
            if remaining_time > 0:
                wait_command(remaining_time / 60, remaining_time / 60)
            log_action("Repeating scenario")
            execute_scenario(scenario_file)
            break
        elif command.startswith("call"):
            scenario_type, scenario_name = command.split()[1].split("_")
            folder = SCENARIO_FOLDERS.get(scenario_type.lower())
            if folder:
                sub_scenario_file = os.path.join(folder, f"{scenario_name}.txt")
                if os.path.exists(sub_scenario_file):
                    log_action(f"Calling scenario: {sub_scenario_file}")
                    execute_scenario(sub_scenario_file)
                else:
                    log_action(f"Error: Scenario file '{sub_scenario_file}' not found.")

        # Insert fillers randomly, but avoid nested fillers
        if not currently_in_filler:
            currently_in_filler = True
            filler_count = random.randint(0, )
            for _ in range(filler_count):
                filler_files = os.listdir(SCENARIO_FOLDERS["fillers"])
                if filler_files:
                    filler_file = random.choice(filler_files)
                    filler_path = os.path.join(SCENARIO_FOLDERS["fillers"], filler_file)
                    log_action(f"Executing filler: {filler_path}")
                    execute_scenario(filler_path)
            currently_in_filler = False

# Background thread to execute the main scenario
def run_main_scenario():
    while not stop_flag:
        current_time = datetime.now()
        if current_time.strftime("%H:%M") == "02:50":
            log_action("Inactive period. Pausing execution.")
            wait_command(11 / 60, 11 / 60)  # Wait from 2:50 to 3:01
        elif (current_time.strftime("%H:%M") > "03:01") & (current_time.strftime("%H:%M") < "03:02"):
            log_action("Executing special login scenario.")
            execute_scenario(SPECIAL_LOGIN_FILE)
        execute_scenario(MAIN_SCENARIO_FILE)

# Stop on keyboard interrupt
def stop_on_keypress():
    def on_press(key):
        global stop_flag
        if key == keyboard.Key.f4 and keyboard.Controller().pressed(keyboard.Key.ctrl):
            stop_flag = True
            print("Stop command received. Exiting.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        scenario_thread = threading.Thread(target=run_main_scenario, daemon=True)
        scenario_thread.start()
        stop_on_keypress()
    except Exception as e:
        log_action(f"Error: {e}")
