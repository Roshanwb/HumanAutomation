"""
Simple GUI for adjusting component mappings.
This helps you visually adjust the screen coordinates for your mapped components.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class MapperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Component Mapper - Adjuster")
        self.root.geometry("600x400")
        
        self.mapping_file = "mapped_components.json"
        self.components = self.load_components()
        
        self.create_widgets()
    
    def load_components(self):
        """Load existing component mappings."""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load mappings: {e}")
        return {}
    
    def save_components(self):
        """Save component mappings."""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.components, f, indent=2)
            messagebox.showinfo("Success", "Mappings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save mappings: {e}")
    
    def create_widgets(self):
        """Create the GUI elements."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Component Mapping Adjuster", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Component list
        list_frame = ttk.LabelFrame(main_frame, text="Mapped Components", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.component_list = tk.Listbox(listbox_frame, height=10)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.component_list.yview)
        self.component_list.configure(yscrollcommand=scrollbar.set)
        
        self.component_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load components into list
        self.refresh_component_list()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Refresh List", 
                  command=self.refresh_component_list).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Edit Selected", 
                  command=self.edit_component).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Save Changes", 
                  command=self.save_components).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def refresh_component_list(self):
        """Refresh the list of components."""
        self.component_list.delete(0, tk.END)
        self.components = self.load_components()
        
        for component_name in self.components.keys():
            self.component_list.insert(tk.END, component_name)
    
    def edit_component(self):
        """Edit the selected component."""
        selection = self.component_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a component to edit.")
            return
        
        component_name = self.component_list.get(selection[0])
        self.open_edit_dialog(component_name)
    
    def open_edit_dialog(self, component_name):
        """Open dialog to edit component coordinates."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit: {component_name}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        component = self.components[component_name]
        bounds = component.get('screenBoundaries', {})
        
        # Coordinate inputs
        ttk.Label(dialog, text="minX:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        minx_var = tk.StringVar(value=str(bounds.get('minX', 0)))
        ttk.Entry(dialog, textvariable=minx_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="minY:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        miny_var = tk.StringVar(value=str(bounds.get('minY', 0)))
        ttk.Entry(dialog, textvariable=miny_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="maxX:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        maxx_var = tk.StringVar(value=str(bounds.get('maxX', 0)))
        ttk.Entry(dialog, textvariable=maxx_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="maxY:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        maxy_var = tk.StringVar(value=str(bounds.get('maxY', 0)))
        ttk.Entry(dialog, textvariable=maxy_var, width=10).grid(row=3, column=1, padx=5, pady=5)
        
        def save_changes():
            try:
                self.components[component_name]['screenBoundaries'] = {
                    'minX': int(minx_var.get()),
                    'minY': int(miny_var.get()),
                    'maxX': int(maxx_var.get()),
                    'maxY': int(maxy_var.get())
                }
                messagebox.showinfo("Success", f"Updated {component_name}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid integer coordinates")
        
        ttk.Button(dialog, text="Save", command=save_changes).grid(row=4, column=0, columnspan=2, pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = MapperGUI(root)
    root.mainloop()