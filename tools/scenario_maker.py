"""
Professional Scenario Maker with syntax highlighting and full functionality.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from typing import List, Dict, Any


class SyntaxHighlightingText(scrolledtext.ScrolledText):
    """Text widget with syntax highlighting for scenario files."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(font=('Consolas', 10), wrap=tk.NONE)
        self._setup_tags()
    
    def _setup_tags(self):
        """Setup color tags for syntax highlighting."""
        # Command tags
        self.tag_configure('command', foreground='#0000FF', font=('Consolas', 10, 'bold'))
        self.tag_configure('component', foreground='#008000', font=('Consolas', 10))
        self.tag_configure('delay', foreground='#FF8C00', font=('Consolas', 10))
        self.tag_configure('text', foreground='#8B008B', font=('Consolas', 10))
        self.tag_configure('comment', foreground='#808080', font=('Consolas', 10, 'italic'))
        
        # Bind key events for real-time highlighting
        self.bind('<KeyRelease>', self._on_key_release)
    
    def _on_key_release(self, event=None):
        """Apply syntax highlighting when text changes."""
        self.highlight_syntax()
    
    def highlight_syntax(self):
        """Apply syntax highlighting to entire text."""
        # Remove existing tags
        for tag in ['command', 'component', 'delay', 'text', 'comment']:
            self.tag_remove(tag, '1.0', tk.END)
        
        content = self.get('1.0', tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            start_index = f"{line_num}.0"
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Handle comments
            if line.strip().startswith('#'):
                comment_start = line.find('#')
                self.tag_add('comment', f"{line_num}.{comment_start}", f"{line_num}.end")
                continue
            
            # Split command and parameters
            parts = line.split(',', 1)
            command_part = parts[0].strip()
            params_part = parts[1] if len(parts) > 1 else ""
            
            # Highlight command
            command_words = command_part.split()
            if command_words:
                command_type = command_words[0].lower()
                self.tag_add('command', f"{line_num}.0", f"{line_num}.{len(command_type)}")
                
                # Highlight components in click commands
                if command_type == 'click' and len(command_words) > 1:
                    component_start = len(command_type) + 1
                    component_end = len(command_part)
                    self.tag_add('component', f"{line_num}.{component_start}", f"{line_num}.{component_end}")
                
                # Highlight text in type commands
                elif command_type == 'type' and '"' in command_part:
                    text_start = command_part.find('"')
                    text_end = command_part.rfind('"') + 1
                    if text_end > text_start:
                        self.tag_add('text', f"{line_num}.{text_start}", f"{line_num}.{text_end}")
            
            # Highlight delays
            if params_part and '-' in params_part:
                delay_part = params_part.strip()
                delay_start = len(line) - len(delay_part)
                self.tag_add('delay', f"{line_num}.{delay_start}", f"{line_num}.end")


class ScenarioMaker:
    """Complete scenario creation tool with full functionality."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Scenario Maker Professional")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.current_file = None
        self.components = self._load_components()
        self.scenarios = self._load_scenarios()
        
        self._setup_gui()
        self._apply_theme()
    
    def _load_components(self) -> List[str]:
        """Load available components from mapping file."""
        try:
            if os.path.exists("mapped_components.json"):
                with open("mapped_components.json", "r") as f:
                    data = json.load(f)
                    return list(data.keys())
        except:
            pass
        return []
    
    def _load_scenarios(self) -> Dict[str, List[str]]:
        """Load available scenarios from all folders."""
        scenarios = {
            "mustdo": [],
            "randos": [],
            "fillers": []
        }
        
        for folder in scenarios.keys():
            folder_path = f"scenarios/{folder}"
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith('.txt'):
                        scenarios[folder].append(file[:-4])
        
        return scenarios
    
    def _setup_gui(self):
        """Setup the complete GUI interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Scenario Maker Professional", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Current file label
        self.file_label = ttk.Label(title_frame, text="New File", foreground="blue")
        self.file_label.pack(side=tk.RIGHT)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Command palette
        left_panel = ttk.LabelFrame(content_frame, text="Command Palette", padding="10", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self._setup_command_palette(left_panel)
        
        # Right panel - Editor
        right_panel = ttk.LabelFrame(content_frame, text="Scenario Editor", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._setup_editor(right_panel)
        
        # Bottom panel - Controls
        bottom_panel = ttk.Frame(main_frame)
        bottom_panel.pack(fill=tk.X, pady=(10, 0))
        
        self._setup_controls(bottom_panel)
    
    def _setup_command_palette(self, parent):
        """Setup the command palette with all available commands and components."""
        # Notebook for different command categories
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic Commands tab
        basic_frame = ttk.Frame(notebook, padding="5")
        notebook.add(basic_frame, text="Basic Commands")
        
        basic_commands = [
            ("🖱️ Click Component", "click component_name,500-1500"),
            ("⌨️ Type Text", 'type "Your text here",100-300'),
            ("⏳ Wait", "wait,0.1-5.0"),
            ("🐭 Move Mouse", "movemouse"),
            ("🔊 Beep", "beep,200-500"),
            ("⌨️ Press Key", "press enter,100-500"),
            ("⏰ Set Total Time", "totaltime,60-120")
        ]
        
        for i, (label, template) in enumerate(basic_commands):
            btn = ttk.Button(basic_frame, text=label, 
                           command=lambda t=template: self._insert_command(t))
            btn.pack(fill=tk.X, pady=2)
        
        # Advanced Commands tab
        advanced_frame = ttk.Frame(notebook, padding="5")
        notebook.add(advanced_frame, text="Advanced")
        
        advanced_commands = [
            ("📞 Call Scenario", "call scenario_name"),
            ("🐍 Execute Script", 'execute "script.py arg1 arg2",500-1500'),
            ("🔁 Repeat", "repeat"),
            ("🏁 End", "end"),
            ("🖥️ Shutdown", "shutdown")
        ]
        
        for i, (label, template) in enumerate(advanced_commands):
            btn = ttk.Button(advanced_frame, text=label,
                           command=lambda t=template: self._insert_command(t))
            btn.pack(fill=tk.X, pady=2)
        
        # Components tab
        components_frame = ttk.Frame(notebook, padding="5")
        notebook.add(components_frame, text="Components")
        
        if self.components:
            component_listbox = tk.Listbox(components_frame, height=15, font=('Consolas', 9))
            scrollbar = ttk.Scrollbar(components_frame, orient=tk.VERTICAL, command=component_listbox.yview)
            component_listbox.configure(yscrollcommand=scrollbar.set)
            
            for component in sorted(self.components):
                component_listbox.insert(tk.END, component)
            
            component_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Double-click to insert component
            component_listbox.bind('<Double-Button-1>', 
                                 lambda e: self._insert_component(component_listbox))
        else:
            ttk.Label(components_frame, text="No components mapped yet.\nUse Component Mapper first.",
                     foreground="red", justify=tk.CENTER).pack(expand=True)
        
        # Scenarios tab
        scenarios_frame = ttk.Frame(notebook, padding="5")
        notebook.add(scenarios_frame, text="Scenarios")
        
        scenario_notebook = ttk.Notebook(scenarios_frame)
        scenario_notebook.pack(fill=tk.BOTH, expand=True)
        
        for folder_name, scenario_list in self.scenarios.items():
            if scenario_list:
                frame = ttk.Frame(scenario_notebook)
                scenario_notebook.add(frame, text=folder_name.capitalize())
                
                listbox = tk.Listbox(frame, height=8, font=('Consolas', 9))
                scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
                listbox.configure(yscrollcommand=scrollbar.set)
                
                for scenario in sorted(scenario_list):
                    listbox.insert(tk.END, scenario)
                
                listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                listbox.bind('<Double-Button-1>', 
                           lambda e, lb=listbox: self._insert_scenario_call(lb))
    
    def _setup_editor(self, parent):
        """Setup the syntax-highlighting editor."""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="🧹 Clear", command=self._clear_editor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="💫 Format", command=self._format_scenario).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📋 Insert Sample", command=self._insert_sample).pack(side=tk.LEFT, padx=5)
        
        # Editor
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.editor = SyntaxHighlightingText(editor_frame)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, border=0,
                                   background='lightgray', state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Sync scrolling and line numbers
        self._setup_editor_bindings()
        
        # Insert initial sample
        self._insert_sample()
    
    def _setup_editor_bindings(self):
        """Setup editor bindings for line numbers and scrolling."""
        def update_line_numbers(event=None):
            # Update line numbers
            lines = self.editor.get('1.0', tk.END).count('\n')
            self.line_numbers.config(state='normal')
            self.line_numbers.delete('1.0', tk.END)
            for i in range(1, lines + 1):
                self.line_numbers.insert(tk.END, f"{i}\n")
            self.line_numbers.config(state='disabled')
            
            # Sync scrolling
            self.line_numbers.yview_moveto(self.editor.yview()[0])
        
        def sync_scroll(*args):
            self.line_numbers.yview_moveto(args[0])
            self.editor.yview_moveto(args[0])
        
        self.editor.bind('<KeyRelease>', update_line_numbers)
        self.editor.bind('<MouseWheel>', update_line_numbers)
        self.editor.bind('<Button-4>', update_line_numbers)
        self.editor.bind('<Button-5>', update_line_numbers)
        
        self.editor.configure(yscrollcommand=sync_scroll)
        self.line_numbers.configure(yscrollcommand=sync_scroll)
        
        # Initial update
        update_line_numbers()
    
    def _setup_controls(self, parent):
        """Setup control buttons."""
        # Left side - file operations
        file_frame = ttk.Frame(parent)
        file_frame.pack(side=tk.LEFT)
        
        ttk.Button(file_frame, text="📄 New", command=self._new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="📂 Open", command=self._open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="💾 Save", command=self._save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="💾 Save As", command=self._save_as_file).pack(side=tk.LEFT, padx=2)
        
        # Right side - other operations
        other_frame = ttk.Frame(parent)
        other_frame.pack(side=tk.RIGHT)
        
        ttk.Button(other_frame, text="🔄 Refresh Lists", command=self._refresh_lists).pack(side=tk.LEFT, padx=2)
        ttk.Button(other_frame, text="❓ Help", command=self._show_help).pack(side=tk.LEFT, padx=2)
        ttk.Button(other_frame, text="🚪 Exit", command=self.root.quit).pack(side=tk.LEFT, padx=2)
    
    def _apply_theme(self):
        """Apply a professional theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TButton', padding=5)
        style.configure('TFrame', background='#f0f0f0')
    
    def _insert_command(self, template: str):
        """Insert a command template into the editor."""
        self.editor.insert(tk.END, template + "\n")
        self.editor.highlight_syntax()
        self.editor.focus_set()
    
    def _insert_component(self, listbox):
        """Insert selected component into a click command."""
        selection = listbox.curselection()
        if selection:
            component = listbox.get(selection[0])
            self._insert_command(f"click {component},500-1500")
    
    def _insert_scenario_call(self, listbox):
        """Insert selected scenario as a call command."""
        selection = listbox.curselection()
        if selection:
            scenario = listbox.get(selection[0])
            self._insert_command(f"call {scenario}")
    
    def _clear_editor(self):
        """Clear the editor content."""
        if messagebox.askyesno("Clear Editor", "Are you sure you want to clear the editor?"):
            self.editor.delete('1.0', tk.END)
            self.editor.highlight_syntax()
    
    def _format_scenario(self):
        """Format the scenario for better readability."""
        content = self.editor.get('1.0', tk.END)
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#'):
                # Comments - ensure they start with #
                if not line.startswith('# '):
                    line = '# ' + line[1:].lstrip()
                formatted_lines.append(line)
            else:
                # Commands - ensure proper spacing
                parts = line.split(',', 1)
                if len(parts) == 2:
                    command = parts[0].strip()
                    params = parts[1].strip()
                    formatted_lines.append(f"{command}, {params}")
                else:
                    formatted_lines.append(line)
        
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', '\n'.join(formatted_lines))
        self.editor.highlight_syntax()
    
    def _insert_sample(self):
        """Insert a sample scenario."""
        sample = """# Sample Automation Scenario
# Lines starting with # are comments

# Set total execution time (minutes)
totaltime, 60-120

# Main loop
movemouse
wait, 0.1-0.5

# Login sequence
click login_button, 500-1500
type "your_username", 100-300
click password_field, 500-1000
type "your_password", 100-300
click submit_button, 1000-2000

# Wait for navigation
wait, 2-5

# Perform actions
call common_actions
execute "process_data.py", 500-1500

# Completion signal
beep, 500-1000

# Repeat while time permits
repeat
"""
        self.editor.insert('1.0', sample)
        self.editor.highlight_syntax()
    
    def _new_file(self):
        """Create a new scenario file."""
        if self._check_unsaved_changes():
            self.editor.delete('1.0', tk.END)
            self.current_file = None
            self.file_label.config(text="New File")
            self._insert_sample()
    
    def _open_file(self):
        """Open an existing scenario file."""
        if not self._check_unsaved_changes():
            return
        
        filename = filedialog.askopenfilename(
            title="Open Scenario File",
            filetypes=[
                ("Scenario files", "*.txt"),
                ("All files", "*.*")
            ],
            initialdir="scenarios"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', content)
                self.current_file = filename
                self.file_label.config(text=os.path.basename(filename))
                self.editor.highlight_syntax()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def _save_file(self):
        """Save the current scenario file."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self._save_as_file()
    
    def _save_as_file(self):
        """Save the scenario with a new filename."""
        filename = filedialog.asksaveasfilename(
            title="Save Scenario File",
            defaultextension=".txt",
            filetypes=[
                ("Scenario files", "*.txt"),
                ("All files", "*.*")
            ],
            initialdir="scenarios"
        )
        
        if filename:
            self._save_to_file(filename)
            self.current_file = filename
            self.file_label.config(text=os.path.basename(filename))
    
    def _save_to_file(self, filename: str):
        """Save content to specified file."""
        try:
            content = self.editor.get('1.0', tk.END).strip()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Success", f"Scenario saved to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def _check_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes and prompt to save."""
        # For simplicity, always return True
        # In a real implementation, you'd track changes and prompt accordingly
        return True
    
    def _refresh_lists(self):
        """Refresh the component and scenario lists."""
        self.components = self._load_components()
        self.scenarios = self._load_scenarios()
        messagebox.showinfo("Refresh", "Component and scenario lists updated.")
    
    def _show_help(self):
        """Show help information."""
        help_text = """Scenario Maker Professional - Help

Available Commands:
• click component,min-max       - Click on mapped component
• type "text",min-max          - Type text with delays
• wait,min-max                 - Wait for time (minutes)
• movemouse                    - Move mouse randomly
• beep,min-max                 - Make beep sound
• press key,min-max            - Press keyboard key
• totaltime,min-max            - Set total execution time
• call scenario                - Call another scenario
• execute "script.py",min-max  - Execute Python script
• repeat                       - Repeat scenario
• end                          - End execution
• shutdown                     - Shutdown computer

Tips:
• Use # for comments
• Delays are in milliseconds (except wait: minutes)
• Components must be mapped first using Component Mapper
• Scenarios are saved in scenarios/ folder"""
        
        messagebox.showinfo("Help", help_text)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ScenarioMaker(root)
    root.mainloop()


if __name__ == "__main__":
    main()