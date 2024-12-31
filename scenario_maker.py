import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import random

# Paths and Data
MAPPED_COMPONENTS_FILE = "mapped_components.json"
SCENARIO_FOLDERS = {
    "mustdo": "mustdo",
    "randos": "randos",
    "fillers": "fillers"
}
DEFAULT_DELAY = "500-1500"

# Load mapped components
def load_mapped_components():
    if os.path.exists(MAPPED_COMPONENTS_FILE):
        with open(MAPPED_COMPONENTS_FILE, "r") as file:
            return json.load(file)
    else:
        messagebox.showerror("Error", f"Mapping file '{MAPPED_COMPONENTS_FILE}' not found.")
        return {}

# Load existing scenarios
def load_scenarios(folder):
    if os.path.exists(folder):
        return [f[:-4] for f in os.listdir(folder) if f.endswith(".txt")]
    else:
        return []

# Create the GUI Application
class ScenarioCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scenario Creator")

        # Load data
        self.mapped_components = load_mapped_components()
        self.mustdo_scenarios = load_scenarios(SCENARIO_FOLDERS["mustdo"])
        self.randos_scenarios = load_scenarios(SCENARIO_FOLDERS["randos"])
        self.fillers_scenarios = load_scenarios(SCENARIO_FOLDERS["fillers"])

        # UI Elements
        self.create_ui()

    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        # Component selection box
        self.create_listbox(main_frame, "Mapped Items", self.mapped_components.keys(), 0, 0)

        # MustDo scenarios
        self.create_listbox(main_frame, "MustDo Scenarios", self.mustdo_scenarios, 0, 1)

        # Randos scenarios
        self.create_listbox(main_frame, "Randos Scenarios", self.randos_scenarios, 0, 2)

        # Fillers scenarios
        self.create_listbox(main_frame, "Fillers Scenarios", self.fillers_scenarios, 0, 3)

        # Wait, TOTALTIME, and TYPE commands
        self.create_listbox(main_frame, "Commands", ["WAIT", "TOTALTIME", "TYPE"], 0, 4)

        # Scenario composition area
        ttk.Label(main_frame, text="Scenario Composition:").grid(row=1, column=0, columnspan=5)
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky="NSEW")
        self.composition_text = tk.Text(text_frame, width=100, height=20, wrap="none")
        text_scrollbar_y = ttk.Scrollbar(text_frame, orient="vertical", command=self.composition_text.yview)
        text_scrollbar_x = ttk.Scrollbar(text_frame, orient="horizontal", command=self.composition_text.xview)
        self.composition_text.configure(yscrollcommand=text_scrollbar_y.set, xscrollcommand=text_scrollbar_x.set)
        self.composition_text.grid(row=0, column=0, sticky="NSEW")
        text_scrollbar_y.grid(row=0, column=1, sticky="NS")
        text_scrollbar_x.grid(row=1, column=0, sticky="EW")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=5, pady=10)

        add_button = ttk.Button(button_frame, text="Add Command", command=self.add_command)
        add_button.grid(row=0, column=0, padx=5)

        load_button = ttk.Button(button_frame, text="Load Scenario", command=self.load_scenario)
        load_button.grid(row=0, column=1, padx=5)

        save_button = ttk.Button(button_frame, text="Save Scenario", command=self.save_scenario)
        save_button.grid(row=0, column=2, padx=5)

    def create_listbox(self, parent, label_text, items, row, col):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="N")

        ttk.Label(frame, text=label_text).pack()
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill="both", expand=True)

        listbox = tk.Listbox(listbox_frame, height=15, width=25, exportselection=False)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        for item in items:
            listbox.insert(tk.END, item)

        # Bind double-click event
        listbox.bind("<Double-Button-1>", lambda e, lb=listbox: self.handle_double_click(lb))

        # Bind single-click toggle selection
        listbox.bind("<Button-1>", lambda e, lb=listbox: self.toggle_selection(lb, e))

        setattr(self, f"{label_text.replace(' ', '_').lower()}_listbox", listbox)

    def clear_all_selections(self):
        for lb_name in ["mapped_items_listbox", "mustdo_scenarios_listbox", "randos_scenarios_listbox", "fillers_scenarios_listbox", "commands_listbox"]:
            lb = getattr(self, lb_name)
            lb.selection_clear(0, tk.END)

    def toggle_selection(self, listbox, event):
        index = listbox.nearest(event.y)
        if listbox.selection_includes(index):
            listbox.selection_clear(index)
        else:
            self.clear_all_selections()
            listbox.selection_set(index)

    def handle_double_click(self, listbox):
        selected = listbox.curselection()
        if selected:
            self.add_command(listbox=listbox)

    def apply_syntax_highlighting(self):
        self.composition_text.tag_configure("command", foreground="blue")
        self.composition_text.tag_configure("component", foreground="green")
        self.composition_text.tag_configure("delay", foreground="orange")
        self.composition_text.tag_configure("text", foreground="purple")

        content = self.composition_text.get("1.0", tk.END)
        self.composition_text.tag_remove("command", "1.0", tk.END)
        self.composition_text.tag_remove("component", "1.0", tk.END)
        self.composition_text.tag_remove("delay", "1.0", tk.END)
        self.composition_text.tag_remove("text", "1.0", tk.END)

        lines = content.splitlines()
        for i, line in enumerate(lines):
            start_index = f"{i+1}.0"
            words = line.split(" ", 1)
            if not words:
                continue
            command = words[0].lower()
            if command in ["click", "type", "call", "wait", "totaltime"]:
                self.composition_text.tag_add("command", start_index, f"{start_index}+{len(command)}c")
            if len(words) > 1:
                remaining = words[1]
                if "," in remaining:  # Handle delay
                    component, delay = remaining.rsplit(",", 1)
                    delay_index = f"{start_index}+{len(line)-len(delay)-1}c"
                    self.composition_text.tag_add("delay", delay_index, f"{delay_index}+{len(delay)}c")
                    self.composition_text.tag_add("component", start_index, f"{delay_index}-1c")
                elif "\"" in remaining:  # Handle text
                    text_index = f"{start_index}+{len(command)+1}c"
                    self.composition_text.tag_add("text", text_index, f"{text_index}+{len(remaining)}c")


    def add_command(self, listbox=None):
        command_type = None
        component = None

        if listbox:  # Directly add from passed listbox
            selected = listbox.curselection()
            if not selected:
                return
            index = selected[0]
            if "mapped_items" in listbox._name:
                command_type = "Click"
                component = listbox.get(index)
            elif "mustdo_scenarios" in listbox._name or "randos_scenarios" in listbox._name or "fillers_scenarios" in listbox._name:
                command_type = "CALL"
                component = listbox.get(index)
            elif "commands" in listbox._name:
                command_type = listbox.get(index)
                if command_type == "WAIT":
                    component = "0.05-0.15"  # Default wait time
                elif command_type == "TOTALTIME":
                    component = "100-120"  # Default total time
                elif command_type == "TYPE":
                    component = "\"Your_Text_Here\""  # Default text placeholder
        else:
            for lb_name in ["mapped_items_listbox", "mustdo_scenarios_listbox", "randos_scenarios_listbox", "fillers_scenarios_listbox", "commands_listbox"]:
                lb = getattr(self, lb_name)
                selected = lb.curselection()
                if selected:
                    index = selected[0]
                    if "mapped_items" in lb_name:
                        command_type = "Click"
                        component = lb.get(index)
                    elif "mustdo_scenarios" in lb_name or "randos_scenarios" in lb_name or "fillers_scenarios" in lb_name:
                        command_type = "CALL"
                        component = lb.get(index)
                    elif "commands" in lb_name:
                        command_type = lb.get(index)
                        if command_type == "WAIT":
                            component = "0.05-0.15"
                        elif command_type == "TOTALTIME":
                            component = "100-120"
                        elif command_type == "TYPE":
                            component = "\"Your_Text_Here\""
                    break

        if not command_type or not component:
            messagebox.showwarning("Warning", "Please select an item to add.")
            return

        if command_type == "Click":
            self.composition_text.insert(tk.END, f"{command_type} {component}, {DEFAULT_DELAY}\n")
        elif command_type == "CALL":
            self.composition_text.insert(tk.END, f"{command_type} {component}\n")
        elif command_type in ["WAIT", "TOTALTIME"]:
            self.composition_text.insert(tk.END, f"{command_type}, {component}\n")
        elif command_type == "TYPE":
            self.composition_text.insert(tk.END, f"{command_type} {component}, {DEFAULT_DELAY}\n")
        self.apply_syntax_highlighting()
        



    def save_scenario(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        content = self.composition_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Composition is empty.")
            return

        with open(file_path, "w") as file:
            file.write(content)

        messagebox.showinfo("Success", f"Scenario saved to {file_path}.")

        # Reload all scenario lists
        self.mustdo_scenarios = load_scenarios(SCENARIO_FOLDERS["mustdo"])
        self.randos_scenarios = load_scenarios(SCENARIO_FOLDERS["randos"])
        self.fillers_scenarios = load_scenarios(SCENARIO_FOLDERS["fillers"])

        self.update_listbox(self.mustdo_scenarios_listbox, self.mustdo_scenarios)
        self.update_listbox(self.randos_scenarios_listbox, self.randos_scenarios)
        self.update_listbox(self.fillers_scenarios_listbox, self.fillers_scenarios)

    def update_listbox(self, listbox, items):
        listbox.delete(0, tk.END)
        for item in items:
            listbox.insert(tk.END, item)

    def load_scenario(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                content = file.read()
            self.composition_text.delete("1.0", tk.END)
            self.composition_text.insert(tk.END, content)
            messagebox.showinfo("Success", f"Scenario loaded from {file_path}.")
            self.apply_syntax_highlighting()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load scenario: {e}")
    
if __name__ == "__main__":
    root = tk.Tk()
    app = ScenarioCreatorApp(root)
    root.mainloop()
