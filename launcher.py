import tkinter as tk
from tkinter import ttk
import subprocess
import os

# Paths to the programs
PROGRAMS = {
    "Run Automation": "run.py",
    "Scenario Maker": "scenario_maker.py",
    "Mapper": "mapper.py"
}

def run_program(program_name):
    program_path = PROGRAMS.get(program_name)
    if not program_path:
        return
    try:
        subprocess.Popen(["python", program_path], shell=True)
    except Exception as e:
        print(f"Error launching {program_name}: {e}")

class ProgramLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automation Program Launcher")
        self.root.geometry("400x300")

        ttk.Label(self.root, text="Select a Program to Run", font=("Arial", 16)).pack(pady=20)

        for program_name in PROGRAMS.keys():
            button = ttk.Button(self.root, text=program_name, command=lambda name=program_name: run_program(name))
            button.pack(pady=10)

        ttk.Label(self.root, text="Created by Insights", font=("Arial", 10, "italic")).pack(side="bottom", pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProgramLauncherApp(root)
    root.mainloop()
