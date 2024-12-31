import pyautogui
import time
import random
import json
import threading
import os
import sys
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
special_login_executed = False
special_login_in_progress = False
last_chrome_tab = None
execution_context = {
    "current_scenario": None,
    "current_line": 0,
    "elapsed_time": 0  # Track elapsed time for TOTALTIME
}


def save_state():
    state = {
        "last_chrome_tab": last_chrome_tab,
        "execution_context": execution_context
    }
    with open("program_state.json", "w") as f:
        json.dump(state, f, indent=4)
    log_action("Program state saved to 'program_state.json'.")

def terminate_threads():
    global stop_flag
    stop_flag = True
    log_action("Stopping background threads...")
    if scenario_thread and scenario_thread.is_alive():
        scenario_thread.join()
    log_action("Background threads stopped.")

def release_resources():
    log_action("Releasing resources...")
    # Stop keyboard listener
    try:
        keyboard.Listener.stop()
    except Exception as e:
        log_action(f"Error releasing resources: {e}")
    log_action("Resources released.")

def shutdown():
    """
    Perform cleanup and gracefully terminate the program.
    """
    log_action("Shutdown process initiated...")
    # Save program state
    save_state()
    # Terminate background threads
    terminate_threads()
    # Release resources
    release_resources()
    log_action("Program terminated successfully.")


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
    execution_context["elapsed_time"] += delay / 60  # Add delay to elapsed time in minutes

# Human-like mouse movement
def human_move_to(target_x, target_y):
    check_special_login()
    start_x, start_y = pyautogui.position()
    steps = random.randint(10, 20)
    control_x1 = start_x + random.randint(-50, 50)
    control_y1 = start_y + random.randint(-50, 50)
    control_x2 = target_x + random.randint(-50, 50)
    control_y2 = target_y + random.randint(-50, 50)

    # Dynamic speed adjustment
    speeds = [random.uniform(0.005, 0.015) for _ in range(steps)]

    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**3 * start_x + 3 * (1 - t)**2 * t * control_x1 + 3 * (1 - t) * t**2 * control_x2 + t**3 * target_x
        y = (1 - t)**3 * start_y + 3 * (1 - t)**2 * t * control_y1 + 3 * (1 - t) * t**2 * control_y2 + t**3 * target_y
        pyautogui.moveTo(x, y, duration=speeds[i % len(speeds)])

    pyautogui.moveTo(target_x, target_y, duration=0.01)
    log_action(f"Moved mouse to ({target_x}, {target_y}) smoothly")

# Random mouse movement
def random_mouse_move():
    check_special_login()
    components = load_mapped_components()
    screen = components.get(WHOLESCREEN_KEY)
    if not screen:
        raise ValueError("WHOLESCREEN boundary not defined in mapping.")

    random_x = random.randint(screen['screenBoundaries']['minX'], screen['screenBoundaries']['maxX'])
    random_y = random.randint(screen['screenBoundaries']['minY'], screen['screenBoundaries']['maxY'])
    human_move_to(random_x, random_y)
    log_action(f"Random mouse move to ({random_x}, {random_y})")

# Human-like typing function
def type_text(text, min_delay, max_delay):
    for char in text:
        pyautogui.typewrite(char)
        delay = random.uniform(min_delay / 1000.0, max_delay / 1000.0)
        time.sleep(delay)
    log_action(f"Typed text: \"{text}\"")



# Click component
def click_component(component_id):
    global last_chrome_tab

    check_special_login()
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

    if not special_login_in_progress and "chrometab" in component_id:
        last_chrome_tab = component
        log_action(f"Last Chrome tab set to: {component_id}")

# Click the last Chrome tab
def click_last_chrome_tab():
    global last_chrome_tab
    if last_chrome_tab:
        x = random.randint(last_chrome_tab['screenBoundaries']['minX'], last_chrome_tab['screenBoundaries']['maxX'])
        y = random.randint(last_chrome_tab['screenBoundaries']['minY'], last_chrome_tab['screenBoundaries']['maxY'])
        human_move_to(x, y)
        pyautogui.click()
        log_action("Clicked on the last Chrome tab.")
    else:
        log_action("No last Chrome tab recorded. Skipping.")

# Wait command
def wait_command(min_minutes, max_minutes):
    check_special_login()
    wait_time = random.uniform(min_minutes * 60, max_minutes * 60)
    for remaining in range(int(wait_time), 0, -1):
        mins, secs = divmod(remaining, 60)
        print(f"Waiting: {mins:02}:{secs:02} remaining", end="\r")
        time.sleep(1)
    print("\n")
    log_action(f"Waited for {wait_time / 60:.2f} minutes")
    execution_context["elapsed_time"] += wait_time / 60  # Add wait time to elapsed time

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

# Check for special login scenario
def check_special_login():
    global special_login_executed, special_login_in_progress, execution_context
    if special_login_in_progress:
        return

    current_time = datetime.now()
    if ("03:01" < current_time.strftime("%H:%M") < "03:10") and not special_login_executed:
        special_login_in_progress = True
        log_action("Executing special login scenario.")
        saved_scenario = execution_context["current_scenario"]
        saved_line = execution_context["current_line"]
        execute_scenario(SPECIAL_LOGIN_FILE)
        special_login_executed = True
        special_login_in_progress = False
        if saved_scenario:
            log_action("Resuming previous scenario.")
            click_last_chrome_tab()
            execute_scenario_from_line(saved_scenario, saved_line)

# Execute a scenario file from a specific line
def execute_scenario_from_line(scenario_file, start_line):
    global stop_flag, currently_in_filler

    with open(scenario_file, "r") as file:
        lines = file.readlines()

    for index, line in enumerate(lines[start_line:], start=start_line):
        if stop_flag:
            break

        execution_context["current_scenario"] = scenario_file
        execution_context["current_line"] = index

        check_special_login()

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
            # Adding the TYPE command in scenario execution
        elif command.startswith("type"):
            text = command.split("\"", 2)[1]  # Extract the text within quotes
            # log_action(f"TEXT FOUND- {text} ")
            min_delay, max_delay = map(int, parts[1].strip().split("-"))
            type_text(text, min_delay, max_delay)
        elif command.startswith("totaltime"):
            min_total, max_total = map(float, parts[1].strip().split("-"))
            iteration_time_limit = random.uniform(min_total, max_total)
            execution_context["elapsed_time"] = 0  # Reset elapsed time
            log_action(f"Set TOTALTIME to {iteration_time_limit:.2f} minutes")
        elif command.startswith("repeat"):
            remaining_time = iteration_time_limit - execution_context["elapsed_time"]
            if remaining_time > 0:
                wait_command(remaining_time, remaining_time)
            log_action("Repeating scenario")
            execute_scenario(scenario_file)
            break
        elif command.startswith("end"):
            log_action("END command encountered.")
            shutdown()
            sys.exit()
        elif command.startswith("shutdown"):
            log_action("ShutDown command encountered. Shutting down gracefully.")            
            os.system("Rundll32.exe Powrprof.dll,SetSuspendState Sleep")
            sys.exit()    
        elif command.startswith("call"):
            sub_scenario_file = find_scenario_file(command.split()[1])
            if sub_scenario_file:
                log_action(f"Calling scenario: {sub_scenario_file}")
                execute_scenario(sub_scenario_file)

        # Insert fillers randomly, but avoid nested fillers
        if not currently_in_filler:
            currently_in_filler = True
            filler_count = random.randint(0, 1)
            for _ in range(filler_count):
                filler_files = os.listdir(SCENARIO_FOLDERS["fillers"])
                if filler_files:
                    filler_file = random.choice(filler_files)
                    filler_path = os.path.join(SCENARIO_FOLDERS["fillers"], filler_file)
                    log_action(f"Executing filler: {filler_path}")
                    execute_scenario(filler_path)
            currently_in_filler = False

# Execute a scenario file
def execute_scenario(scenario_file):
    execute_scenario_from_line(scenario_file, 0)

# Find scenario file
def find_scenario_file(scenario_name):
    found_file = None
    is_randos = False

    for folder_key, folder_path in SCENARIO_FOLDERS.items():
        candidate = os.path.join(folder_path, f"{scenario_name}.txt")
        if os.path.exists(candidate):
            if folder_key == "randos":  # Check if it's a `randos` folder
                is_randos = True
                should_execute = random.choice([True, False])  # 50% chance
                if should_execute:
                    log_action(f"Executing randos scenario: {scenario_name}")
                    return candidate
                else:
                    log_action(f"Skipping randos scenario: {scenario_name}")
                    continue  # Skip this `randos` file
            else:
                # Non-randos file found
                found_file = candidate

    # If no `randos` scenario was executed, return the first non-randos file
    if found_file:
        return found_file

    log_action(f"Error: Scenario file for '{scenario_name}' not found.")
    return None


# Background thread to execute the main scenario
def run_main_scenario():
    while not stop_flag:
        click_last_chrome_tab()
        execute_scenario(MAIN_SCENARIO_FILE)

# Stop on keyboard interrupt
def stop_on_keypress():
    def on_press(key):
        global stop_flag
        if key == keyboard.Key.f4 and keyboard.Controller().pressed(keyboard.Key.ctrl):
            stop_flag = True
            log_action("Stop command received. Exiting...")
            shutdown()  # Call shutdown before exit
            sys.exit()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        scenario_thread = threading.Thread(target=run_main_scenario, daemon=True)
        scenario_thread.start()
        stop_on_keypress()
    except Exception as e:
        log_action(f"Error: {e}")
