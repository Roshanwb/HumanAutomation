"""
Professional Mapper Adjuster with screen overlay and visual component editing.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from typing import Dict, Any, Optional, Tuple
import pyautogui
from screeninfo import get_monitors


class ScreenOverlayApp:
    """Advanced component mapping adjuster with visual overlay."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mapper Adjuster Professional")
        self.root.geometry("900x700")
        
        self.mapping_file = "mapped_components.json"
        self.components = self._load_components()
        self.selected_component = None
        self.overlay_windows = {}
        
        self._setup_gui()
    
    def _load_components(self) -> Dict[str, Any]:
        """Load components with error handling."""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            else:
                messagebox.showerror("Error", f"Mapping file not found: {self.mapping_file}")
                return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load components: {e}")
            return {}
    
    def _save_components(self):
        """Save components with error handling."""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.components, f, indent=2)
            messagebox.showinfo("Success", "Components saved successfully!")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save components: {e}")
            return False
    
    def _setup_gui(self):
        """Setup the main GUI interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Mapper Adjuster Professional", 
                 font=('Arial', 16, 'bold')).pack()
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Component list
        left_panel = ttk.LabelFrame(content_frame, text="Components", padding="10", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self._setup_component_list(left_panel)
        
        # Right panel - Controls and info
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._setup_controls(right_panel)
        self._setup_component_info(right_panel)
    
    def _setup_component_list(self, parent):
        """Setup the component list with search and filter."""
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        search_entry.bind('<KeyRelease>', lambda e: self._filter_components(search_var.get()))
        
        # Component list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.component_listbox = tk.Listbox(list_frame, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.component_listbox.yview)
        self.component_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.component_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.component_listbox.bind('<<ListboxSelect>>', self._on_component_select)
        
        # Populate list
        self._refresh_component_list()
    
    def _setup_controls(self, parent):
        """Setup control buttons."""
        controls_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Screen selection
        screen_frame = ttk.Frame(controls_frame)
        screen_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(screen_frame, text="Screen:").pack(side=tk.LEFT)
        self.screen_var = tk.StringVar()
        screen_combo = ttk.Combobox(screen_frame, textvariable=self.screen_var, state="readonly")
        screen_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        screen_combo.bind('<<ComboboxSelected>>', self._on_screen_select)
        
        # Get available screens
        screens = self._get_available_screens()
        screen_combo['values'] = [f"Screen {i+1}: {w}x{h}" for i, (w, h, x, y) in enumerate(screens)]
        if screens:
            screen_combo.current(0)
            self.current_screen = screens[0]
        
        # Control buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="👁️ Show Overlay", 
                  command=self._show_overlay).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="👁️ Show All", 
                  command=self._show_all_overlays).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🙈 Hide All", 
                  command=self._hide_all_overlays).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self._refresh_all).pack(side=tk.RIGHT, padx=(5, 0))
    
    def _setup_component_info(self, parent):
        """Setup component information and editing controls."""
        info_frame = ttk.LabelFrame(parent, text="Component Details", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Component name
        name_frame = ttk.Frame(info_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, state='readonly')
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Boundary controls
        bounds_frame = ttk.Frame(info_frame)
        bounds_frame.pack(fill=tk.X, pady=5)
        
        # minX control
        minx_frame = ttk.Frame(bounds_frame)
        minx_frame.pack(fill=tk.X, pady=2)
        ttk.Label(minx_frame, text="minX:", width=8).pack(side=tk.LEFT)
        self.minx_var = tk.StringVar()
        minx_entry = ttk.Entry(minx_frame, textvariable=self.minx_var, width=10)
        minx_entry.pack(side=tk.LEFT)
        ttk.Button(minx_frame, text="▲", width=3, 
                  command=lambda: self._adjust_boundary('minX', 1)).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Button(minx_frame, text="▼", width=3,
                  command=lambda: self._adjust_boundary('minX', -1)).pack(side=tk.LEFT)
        
        # minY control
        miny_frame = ttk.Frame(bounds_frame)
        miny_frame.pack(fill=tk.X, pady=2)
        ttk.Label(miny_frame, text="minY:", width=8).pack(side=tk.LEFT)
        self.miny_var = tk.StringVar()
        miny_entry = ttk.Entry(miny_frame, textvariable=self.miny_var, width=10)
        miny_entry.pack(side=tk.LEFT)
        ttk.Button(miny_frame, text="▲", width=3,
                  command=lambda: self._adjust_boundary('minY', 1)).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Button(miny_frame, text="▼", width=3,
                  command=lambda: self._adjust_boundary('minY', -1)).pack(side=tk.LEFT)
        
        # maxX control
        maxx_frame = ttk.Frame(bounds_frame)
        maxx_frame.pack(fill=tk.X, pady=2)
        ttk.Label(maxx_frame, text="maxX:", width=8).pack(side=tk.LEFT)
        self.maxx_var = tk.StringVar()
        maxx_entry = ttk.Entry(maxx_frame, textvariable=self.maxx_var, width=10)
        maxx_entry.pack(side=tk.LEFT)
        ttk.Button(maxx_frame, text="▲", width=3,
                  command=lambda: self._adjust_boundary('maxX', 1)).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Button(maxx_frame, text="▼", width=3,
                  command=lambda: self._adjust_boundary('maxX', -1)).pack(side=tk.LEFT)
        
        # maxY control
        maxy_frame = ttk.Frame(bounds_frame)
        maxy_frame.pack(fill=tk.X, pady=2)
        ttk.Label(maxy_frame, text="maxY:", width=8).pack(side=tk.LEFT)
        self.maxy_var = tk.StringVar()
        maxy_entry = ttk.Entry(maxy_frame, textvariable=self.maxy_var, width=10)
        maxy_entry.pack(side=tk.LEFT)
        ttk.Button(maxy_frame, text="▲", width=3,
                  command=lambda: self._adjust_boundary('maxY', 1)).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Button(maxy_frame, text="▼", width=3,
                  command=lambda: self._adjust_boundary('maxY', -1)).pack(side=tk.LEFT)
        
        # Bind entry changes
        for var, coord in [(self.minx_var, 'minX'), (self.miny_var, 'minY'),
                          (self.maxx_var, 'maxX'), (self.maxy_var, 'maxY')]:
            var.trace('w', lambda *args, c=coord: self._on_boundary_change(c))
        
        # Component info
        info_text_frame = ttk.Frame(info_frame)
        info_text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.info_text = tk.Text(info_text_frame, height=8, wrap=tk.WORD, state='disabled')
        scrollbar = ttk.Scrollbar(info_text_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = ttk.Frame(info_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="💾 Save Changes", 
                  command=self._save_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📊 Backup", 
                  command=self._create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🧪 Test Click", 
                  command=self._test_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🗑️ Delete", 
                  command=self._delete_component).pack(side=tk.RIGHT)
    
    def _get_available_screens(self) -> list:
        """Get available screen information."""
        try:
            screens = []
            for monitor in get_monitors():
                screens.append((monitor.width, monitor.height, monitor.x, monitor.y))
            return screens
        except:
            # Fallback to primary screen
            width, height = pyautogui.size()
            return [(width, height, 0, 0)]
    
    def _refresh_component_list(self, filter_text: str = ""):
        """Refresh the component list with optional filtering."""
        self.component_listbox.delete(0, tk.END)
        
        components = sorted(self.components.keys())
        if filter_text:
            components = [c for c in components if filter_text.lower() in c.lower()]
        
        for component in components:
            self.component_listbox.insert(tk.END, component)
    
    def _filter_components(self, filter_text: str):
        """Filter components based on search text."""
        self._refresh_component_list(filter_text)
    
    def _on_component_select(self, event):
        """Handle component selection."""
        selection = self.component_listbox.curselection()
        if not selection:
            return
        
        component_name = self.component_listbox.get(selection[0])
        self.selected_component = component_name
        self._update_component_info()
    
    def _on_screen_select(self, event):
        """Handle screen selection."""
        if hasattr(self, 'current_screen'):
            # Update overlays for new screen
            pass
    
    def _update_component_info(self):
        """Update component information display."""
        if not self.selected_component or self.selected_component not in self.components:
            return
        
        component = self.components[self.selected_component]
        bounds = component.get('screenBoundaries', {})
        
        # Update name
        self.name_var.set(self.selected_component)
        
        # Update boundary values
        self.minx_var.set(str(bounds.get('minX', 0)))
        self.miny_var.set(str(bounds.get('minY', 0)))
        self.maxx_var.set(str(bounds.get('maxX', 0)))
        self.maxy_var.set(str(bounds.get('maxY', 0)))
        
        # Update info text
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', tk.END)
        
        info = f"Component: {self.selected_component}\n"
        info += f"Position: ({bounds.get('minX', 0)}, {bounds.get('minY', 0)}) to ({bounds.get('maxX', 0)}, {bounds.get('maxY', 0)})\n"
        info += f"Size: {bounds.get('maxX', 0) - bounds.get('minX', 0)} x {bounds.get('maxY', 0) - bounds.get('minY', 0)} pixels\n"
        
        self.info_text.insert('1.0', info)
        self.info_text.config(state='disabled')
    
    def _adjust_boundary(self, boundary: str, delta: int):
        """Adjust boundary value."""
        if not self.selected_component:
            return
        
        bounds = self.components[self.selected_component].get('screenBoundaries', {})
        current_value = bounds.get(boundary, 0)
        new_value = current_value + delta
        
        bounds[boundary] = new_value
        
        # Update display
        if boundary == 'minX':
            self.minx_var.set(str(new_value))
        elif boundary == 'minY':
            self.miny_var.set(str(new_value))
        elif boundary == 'maxX':
            self.maxx_var.set(str(new_value))
        elif boundary == 'maxY':
            self.maxy_var.set(str(new_value))
        
        # Update overlay
        self._update_overlay(self.selected_component)
    
    def _on_boundary_change(self, boundary: str):
        """Handle manual boundary value changes."""
        if not self.selected_component:
            return
        
        try:
            bounds = self.components[self.selected_component].get('screenBoundaries', {})
            
            if boundary == 'minX':
                new_value = int(self.minx_var.get())
            elif boundary == 'minY':
                new_value = int(self.miny_var.get())
            elif boundary == 'maxX':
                new_value = int(self.maxx_var.get())
            elif boundary == 'maxY':
                new_value = int(self.maxy_var.get())
            else:
                return
            
            bounds[boundary] = new_value
            self._update_overlay(self.selected_component)
            
        except ValueError:
            pass  # Invalid input, ignore
    
    def _show_overlay(self):
        """Show overlay for selected component."""
        if not self.selected_component:
            messagebox.showwarning("Warning", "Please select a component first")
            return
        
        self._create_overlay(self.selected_component)
    
    def _show_all_overlays(self):
        """Show overlays for all components."""
        for component_name in self.components.keys():
            self._create_overlay(component_name)
    
    def _hide_all_overlays(self):
        """Hide all overlays."""
        for window in self.overlay_windows.values():
            try:
                window.destroy()
            except:
                pass
        self.overlay_windows.clear()
    
    def _create_overlay(self, component_name: str):
        """Create an overlay window for a component."""
        if component_name in self.overlay_windows:
            try:
                self.overlay_windows[component_name].destroy()
            except:
                pass
        
        component = self.components[component_name]
        bounds = component.get('screenBoundaries', {})
        
        # Create overlay window
        overlay = tk.Toplevel(self.root)
        overlay.title(f"Overlay: {component_name}")
        overlay.attributes('-topmost', True)
        overlay.attributes('-alpha', 0.7)
        
        # Position and size
        min_x = bounds.get('minX', 0)
        min_y = bounds.get('minY', 0)
        max_x = bounds.get('maxX', 0)
        max_y = bounds.get('maxY', 0)
        
        width = max_x - min_x
        height = max_y - min_y
        
        overlay.geometry(f"{width}x{height}+{min_x}+{min_y}")
        overlay.overrideredirect(True)
        
        # Create canvas
        canvas = tk.Canvas(overlay, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw rectangle
        canvas.create_rectangle(0, 0, width, height, outline='red', width=3, fill='red', stipple='gray50')
        
        # Add component name
        canvas.create_text(width//2, height//2, text=component_name, fill='white', font=('Arial', 12, 'bold'))
        
        self.overlay_windows[component_name] = overlay
    
    def _update_overlay(self, component_name: str):
        """Update an existing overlay."""
        if component_name in self.overlay_windows:
            self._create_overlay(component_name)  # Recreate with new bounds
    
    def _refresh_all(self):
        """Refresh all data and displays."""
        self.components = self._load_components()
        self._refresh_component_list()
        self._hide_all_overlays()
        messagebox.showinfo("Refresh", "All data refreshed successfully")
    
    def _save_changes(self):
        """Save all changes."""
        if self._save_components():
            self._refresh_all()
    
    def _create_backup(self):
        """Create a backup of the mapping file."""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"mapped_components_backup_{timestamp}.json"
        
        try:
            shutil.copy2(self.mapping_file, backup_file)
            messagebox.showinfo("Backup", f"Backup created: {backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {e}")
    
    def _test_click(self):
        """Test click on selected component."""
        if not self.selected_component:
            messagebox.showwarning("Warning", "Please select a component first")
            return
        
        component = self.components[self.selected_component]
        bounds = component.get('screenBoundaries', {})
        
        # Calculate center point
        center_x = (bounds.get('minX', 0) + bounds.get('maxX', 0)) // 2
        center_y = (bounds.get('minY', 0) + bounds.get('maxY', 0)) // 2
        
        try:
            # Move to position
            pyautogui.moveTo(center_x, center_y, duration=0.5)
            # Click
            pyautogui.click()
            messagebox.showinfo("Test Click", f"Clicked at ({center_x}, {center_y})")
        except Exception as e:
            messagebox.showerror("Test Error", f"Failed to test click: {e}")
    
    def _delete_component(self):
        """Delete selected component."""
        if not self.selected_component:
            messagebox.showwarning("Warning", "Please select a component first")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete component '{self.selected_component}'?"):
            del self.components[self.selected_component]
            self._save_components()
            self._refresh_all()
            messagebox.showinfo("Success", f"Component '{self.selected_component}' deleted")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ScreenOverlayApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()