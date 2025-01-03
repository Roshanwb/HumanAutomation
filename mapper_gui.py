import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import json
from screeninfo import get_monitors 
import shutil
from datetime import datetime



# File path for the mapping JSON
MAPPING_FILE = "mapped_components.json"


class ScreenOverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapping Adjuster")
        self.mapping = self.load_mapping()
        self.selected_id = None
        self.selected_screen = None
        self.screen_resolution = None
        self.rect = None  # Current rectangle
        self.canvas = None  # Current canvas
        self.overlay = None  # Overlay window reference

        # GUI Layout
        self.create_ui()

    def load_mapping(self):
        """Load the mapping JSON file."""
        if not os.path.exists(MAPPING_FILE):
            messagebox.showerror("Error", f"Mapping file '{MAPPING_FILE}' not found.")
            self.root.quit()
        with open(MAPPING_FILE, "r") as file:
            return json.load(file)

    def save_mapping(self):
        """Save the updated mapping to JSON file."""
        with open(MAPPING_FILE, "w") as file:
            json.dump(self.mapping, file, indent=4)
        #messagebox.showinfo("Success", "Mapping updated and saved.")

    def create_ui(self):
        """Create the main UI layout."""
        # Top frame for screen selection
        top_frame = tk.Frame(self.root, bg="lightgrey", height=40)
        top_frame.pack(side="top", fill="x")

        tk.Label(top_frame, text="Select Screen:", bg="lightgrey", font=("Arial", 12)).pack(side="left", padx=10)
        self.screen_selector = ttk.Combobox(top_frame, state="readonly", font=("Arial", 10))
        self.screen_selector.pack(side="left", padx=10)
        self.screen_selector.bind("<<ComboboxSelected>>", self.on_screen_select)

        # Populate screen options
        self.screens = self.get_screens()
        self.screen_selector["values"] = [f"Screen {i+1}: {screen['width']}x{screen['height']}" for i, screen in enumerate(self.screens)]
        self.screen_selector.current(0)  # Default to the first screen

        # Sidebar for component IDs
        sidebar = tk.Frame(self.root, width=200, bg="lightgrey")
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Component IDs", bg="lightgrey", font=("Arial", 12, "bold")).pack(pady=10)
        self.id_listbox = tk.Listbox(sidebar, selectmode="single", font=("Arial", 10), width=25)
        self.id_listbox.pack(fill="y", padx=10, pady=10, expand=True)
        self.id_listbox.bind("<<ListboxSelect>>", self.on_select_id)
        self.id_listbox.bind("<Double-Button-1>", self.on_double_click)  # Bind double-click
        
        # Load IDs into the listbox
        for component_id in self.mapping.keys():
            self.id_listbox.insert(tk.END, component_id)

        # Controls for rectangle adjustment
        control_frame = tk.Frame(self.root, bg="lightgrey", height=40)
        control_frame.pack(side="bottom", fill="x")

        # Add input fields and buttons for rectangle boundaries
        self.add_boundary_controls(control_frame)

        # Buttons
        button_frame = tk.Frame(self.root, bg="lightgrey")
        button_frame.pack(side="bottom", fill="x", pady=5)

        tk.Button(button_frame, text="Show Overlay", command=self.show_overlay).pack(side="left", padx=5)
        tk.Button(button_frame, text="Hide Overlay", command=self.hide_overlay).pack(side="left", padx=5)  # New
        tk.Button(button_frame, text="Save Changes", command=self.save_mapping).pack(side="left", padx=5)
        tk.Button(button_frame, text="Backup JSON", command=self.backup_json).pack(side="left", padx=5)  # New
        tk.Button(button_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)

    def hide_overlay(self):
        """Hide the overlay window."""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def backup_json(self):
        """Create a backup of the JSON file."""
        backup_dir = "Backup"
        os.makedirs(backup_dir, exist_ok=True)  # Ensure the backups folder exists
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"mapped_components_backup_{timestamp}.json")

        try:
            shutil.copy(MAPPING_FILE, backup_path)
            messagebox.showinfo("Backup", f"Backup created: {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {e}")

    def add_boundary_controls(self, frame):
        """Add controls to adjust rectangle boundaries."""
        tk.Label(frame, text="minX:").grid(row=0, column=0, padx=5, pady=5)
        self.minX_entry = tk.Entry(frame, width=8)
        self.minX_entry.grid(row=0, column=1)
        tk.Button(frame, text="↑", command=lambda: self.adjust_boundary("minX", 1)).grid(row=0, column=2)
        tk.Button(frame, text="↓", command=lambda: self.adjust_boundary("minX", -1)).grid(row=0, column=3)

        tk.Label(frame, text="minY:").grid(row=1, column=0, padx=5, pady=5)
        self.minY_entry = tk.Entry(frame, width=8)
        self.minY_entry.grid(row=1, column=1)
        tk.Button(frame, text="↑", command=lambda: self.adjust_boundary("minY", 1)).grid(row=1, column=2)
        tk.Button(frame, text="↓", command=lambda: self.adjust_boundary("minY", -1)).grid(row=1, column=3)

        tk.Label(frame, text="maxX:").grid(row=2, column=0, padx=5, pady=5)
        self.maxX_entry = tk.Entry(frame, width=8)
        self.maxX_entry.grid(row=2, column=1)
        tk.Button(frame, text="↑", command=lambda: self.adjust_boundary("maxX", 1)).grid(row=2, column=2)
        tk.Button(frame, text="↓", command=lambda: self.adjust_boundary("maxX", -1)).grid(row=2, column=3)

        tk.Label(frame, text="maxY:").grid(row=3, column=0, padx=5, pady=5)
        self.maxY_entry = tk.Entry(frame, width=8)
        self.maxY_entry.grid(row=3, column=1)
        tk.Button(frame, text="↑", command=lambda: self.adjust_boundary("maxY", 1)).grid(row=3, column=2)
        tk.Button(frame, text="↓", command=lambda: self.adjust_boundary("maxY", -1)).grid(row=3, column=3)

    def adjust_boundary(self, boundary, step):
        """Adjust the specified boundary by a step."""
        if not self.rect or not self.selected_id:
            return

        bounds = self.mapping[self.selected_id]["screenBoundaries"]
        current_value = bounds.get(boundary, 0)
        new_value = current_value + step
        bounds[boundary] = new_value

        # Update rectangle and input fields
        self.update_rectangle()
        self.update_boundary_entries()

    def update_boundary_entries(self):
        """Update the text boxes to show current boundary values."""
        if not self.rect or not self.selected_id:
            return

        bounds = self.mapping[self.selected_id]["screenBoundaries"]
        self.minX_entry.delete(0, tk.END)
        self.minX_entry.insert(0, bounds["minX"])
        self.minY_entry.delete(0, tk.END)
        self.minY_entry.insert(0, bounds["minY"])
        self.maxX_entry.delete(0, tk.END)
        self.maxX_entry.insert(0, bounds["maxX"])
        self.maxY_entry.delete(0, tk.END)
        self.maxY_entry.insert(0, bounds["maxY"])

    def update_rectangle(self):
        """Update the rectangle on the canvas based on boundary values."""
        if not self.rect or not self.selected_id or not self.canvas:
            return

        bounds = self.mapping[self.selected_id]["screenBoundaries"]
        self.canvas.coords(self.rect, bounds["minX"], bounds["minY"], bounds["maxX"], bounds["maxY"])

    def get_screens(self):
        """Get the resolutions of all available screens."""
        return [{"width": monitor.width, "height": monitor.height, "x": monitor.x, "y": monitor.y} for monitor in get_monitors()]

    def on_screen_select(self, event):
        """Handle screen selection."""
        selected_index = self.screen_selector.current()
        self.selected_screen = self.screens[selected_index]
        self.screen_resolution = (self.selected_screen["width"], self.selected_screen["height"])

    def on_select_id(self, event):
        """Handle component selection."""
        selection = self.id_listbox.curselection()
        if not selection:
            return
        self.selected_id = self.id_listbox.get(selection[0])

    def show_overlay(self):
        """Show the overlay for the selected component."""
        if not self.selected_id:
            messagebox.showerror("Error", "No component selected.")
            return

        if not self.selected_screen:
            messagebox.showerror("Error", "No screen selected. Please select a screen.")
            return

        component = self.mapping.get(self.selected_id)
        if not component:
            messagebox.showerror("Error", f"Component '{self.selected_id}' not found in mapping.")
            return

        bounds = component.get("screenBoundaries")
        if not bounds:
            messagebox.showerror("Error", f"No boundaries defined for '{self.selected_id}'.")
            return

        # Close existing overlay if it exists
        if self.overlay:
            self.overlay.destroy()

        # Create an overlay window
        self.overlay = tk.Toplevel(self.root)
        self.overlay.geometry(f"{self.screen_resolution[0]}x{self.screen_resolution[1]}+{self.selected_screen['x']}+{self.selected_screen['y']}")
        self.overlay.overrideredirect(True)  # Remove title bar
        self.overlay.attributes("-topmost", True)  # Keep on top
        self.overlay.attributes("-alpha", 0.5)  # Set opacity for transparency

        self.canvas = tk.Canvas(self.overlay, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Draw the rectangle
        self.rect = self.canvas.create_rectangle(
            bounds["minX"], bounds["minY"], bounds["maxX"], bounds["maxY"],
            outline="red", width=2, tags="overlay"
        )

        # Bind keys and mouse actions for adjustment
        self.make_rectangle_editable(self.rect, bounds)

        tk.Button(self.overlay, text="Save Changes", command=self.save_overlay_changes).pack(side="bottom", pady=5)

    def make_rectangle_editable(self, rect, bounds):
        """Enable dragging and resizing of the rectangle."""
        def on_drag(event):
            x1, y1, x2, y2 = self.canvas.coords(rect)
            dx, dy = event.x - x1, event.y - y1
            self.canvas.move(rect, dx, dy)
            x1, y1, x2, y2 = self.canvas.coords(rect)
            bounds["minX"], bounds["minY"], bounds["maxX"], bounds["maxY"] = int(x1), int(y1), int(x2), int(y2)

        def on_key(event):
            dx, dy = 0, 0
            if event.keysym == "Left":
                dx = -1
            elif event.keysym == "Right":
                dx = 1
            elif event.keysym == "Up":
                dy = -1
            elif event.keysym == "Down":
                dy = 1
            self.canvas.move(rect, dx, dy)
            x1, y1, x2, y2 = self.canvas.coords(rect)
            bounds["minX"], bounds["minY"], bounds["maxX"], bounds["maxY"] = int(x1), int(y1), int(x2), int(y2)

        self.canvas.tag_bind(rect, "<B1-Motion>", on_drag)
        self.overlay.bind("<Key>", on_key)
        self.overlay.focus_set()

    def save_overlay_changes(self):
        """Save changes to the JSON mapping."""
        if not self.selected_id or not self.rect:
            return

        bounds = self.canvas.coords(self.rect)
        self.mapping[self.selected_id]["screenBoundaries"] = {
            "minX": int(bounds[0]),
            "minY": int(bounds[1]),
            "maxX": int(bounds[2]),
            "maxY": int(bounds[3])
        }

        self.save_mapping()
        self.overlay.destroy()
        self.overlay = None
    def on_select_id(self, event):
        """Handle component selection."""
        selection = self.id_listbox.curselection()
        if not selection:
            return
        self.selected_id = self.id_listbox.get(selection[0])

    def on_double_click(self, event):
        """Handle double-click on the list item to show overlay."""
        self.on_select_id(event)  # Ensure the selected_id is set
        self.show_overlay()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenOverlayApp(root)
    root.mainloop()
