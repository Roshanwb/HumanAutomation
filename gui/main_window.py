"""
Simple modern GUI for our automation system.
Uses tkinter but makes it look professional.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import Optional

from core.application import HumanAutomationApp
from core.events import event_bus


class ModernButton(ttk.Button):
    """A modern-looking button with consistent styling."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.style = ttk.Style()
        self.style.configure('Modern.TButton', padding=10)


class StatusDisplay(scrolledtext.ScrolledText):
    """A text display for showing status messages."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            wrap=tk.WORD,
            state='disabled',
            height=15,
            background='#f8f9fa',
            foreground='#212529',
            font=('Consolas', 10),
            **kwargs
        )
    
    def add_message(self, message: str, message_type: str = "info"):
        """Add a message with colored formatting."""
        self.config(state='normal')
        
        # Color coding based on message type
        colors = {
            'info': '#000000',
            'success': '#198754',
            'warning': '#ffc107',
            'error': '#dc3545',
            'command': '#0d6efd'
        }
        
        color = colors.get(message_type, '#000000')
        tag_name = f"color_{message_type}"
        
        # Create tag if it doesn't exist
        if tag_name in self.tag_names():
            self.tag_configure(tag_name, foreground=color)
        
        # Add the message
        self.insert(tk.END, f"{message}\n", tag_name)
        self.see(tk.END)
        self.config(state='disabled')


class MainWindow:
    """
    Main application window with clean, modern interface.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.app: Optional[HumanAutomationApp] = None
        
        self._setup_window()
        self._create_widgets()
        self._initialize_app()
        self._setup_event_listeners()
    
    def _setup_window(self):
        """Configure the main window."""
        self.root.title("HumanAutomation Pro")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Center the window on screen
        self.root.eval('tk::PlaceWindow . center')
        
        # Modern style
        self.style = ttk.Style()
        self.style.theme_use('clam')
    
    def _create_widgets(self):
        """Create all the UI elements."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🤖 HumanAutomation Professional",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Automation Control", padding="15")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Control buttons
        self.start_btn = ModernButton(
            control_frame,
            text="▶️ Start Automation",
            command=self._start_automation
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.pause_btn = ModernButton(
            control_frame,
            text="⏸️ Pause",
            command=self._pause_automation,
            state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=10)
        
        self.stop_btn = ModernButton(
            control_frame,
            text="🛑 Stop",
            command=self._stop_automation,
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=2, padx=10)
        
        self.emergency_btn = ModernButton(
            control_frame,
            text="🚨 Emergency Stop",
            command=self._emergency_stop,
            style="Emergency.TButton"
        )
        self.emergency_btn.grid(row=0, column=3, padx=(10, 0))
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="Execution Log", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        self.status_display = StatusDisplay(status_frame)
        self.status_display.grid(row=0, column=0, sticky="nsew")
        
        # Status bar at bottom
        self.status_bar = ttk.Label(main_frame, text="Ready to start", relief="sunken")
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
    
    def _initialize_app(self):
        """Initialize the automation application."""
        self.status_display.add_message("Initializing HumanAutomation...", "info")
        
        try:
            self.app = HumanAutomationApp()
            self.status_display.add_message("✅ Application initialized successfully!", "success")
            self.status_bar.config(text="Ready - Press 'Start Automation' to begin")
        except Exception as e:
            self.status_display.add_message(f"❌ Failed to initialize: {e}", "error")
            self.status_bar.config(text="Initialization failed")
    
    def _setup_event_listeners(self):
        """Set up event listeners for application events."""
        event_bus.subscribe("automation_started", self._on_automation_started)
        event_bus.subscribe("automation_stopped", self._on_automation_stopped)
        event_bus.subscribe("automation_paused", self._on_automation_paused)
        event_bus.subscribe("automation_resumed", self._on_automation_resumed)
        event_bus.subscribe("command_executed", self._on_command_executed)
    
    def _start_automation(self):
        """Start automation when button is clicked."""
        if self.app:
            self.app.start_automation()
    
    def _pause_automation(self):
        """Pause or resume automation."""
        if self.app:
            self.app.pause_automation()
    
    def _stop_automation(self):
        """Stop automation."""
        if self.app:
            self.app.stop_automation()
    
    def _emergency_stop(self):
        """Emergency stop."""
        if self.app:
            self.app.emergency_stop()
    
    def _on_automation_started(self, data=None):
        """Update UI when automation starts."""
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.status_bar.config(text="Automation running...")
        self.status_display.add_message("=== AUTOMATION STARTED ===", "success")
    
    def _on_automation_stopped(self, data=None):
        """Update UI when automation stops."""
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.pause_btn.config(text="⏸️ Pause")
        self.status_bar.config(text="Automation stopped")
        self.status_display.add_message("=== AUTOMATION STOPPED ===", "warning")
    
    def _on_automation_paused(self, data=None):
        """Update UI when automation is paused."""
        self.pause_btn.config(text="▶️ Resume")
        self.status_bar.config(text="Automation paused")
        self.status_display.add_message("=== AUTOMATION PAUSED ===", "warning")
    
    def _on_automation_resumed(self, data=None):
        """Update UI when automation is resumed."""
        self.pause_btn.config(text="⏸️ Pause")
        self.status_bar.config(text="Automation running...")
        self.status_display.add_message("=== AUTOMATION RESUMED ===", "success")
    
    def _on_command_executed(self, data=None):
        """Update UI when a command is executed."""
        if data:
            command = data['command']
            number = data['number']
            total = data['total']
            self.status_display.add_message(f"✅ Executed {command} ({number}/{total})", "command")
            self.status_bar.config(text=f"Running... {number}/{total} commands completed")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

# Add these event listeners to the _setup_event_listeners method:
    def _setup_event_listeners(self):
        """Set up event listeners for application events."""
        event_bus.subscribe("automation_started", self._on_automation_started)
        event_bus.subscribe("automation_stopped", self._on_automation_stopped)
        event_bus.subscribe("automation_paused", self._on_automation_paused)
        event_bus.subscribe("automation_resumed", self._on_automation_resumed)
        event_bus.subscribe("command_executed", self._on_command_executed)
        event_bus.subscribe("command_started", self._on_command_started)
        event_bus.subscribe("scenario_loaded", self._on_scenario_loaded)
        event_bus.subscribe("scenario_completed", self._on_scenario_completed)
        event_bus.subscribe("automation_error", self._on_automation_error)
        event_bus.subscribe("total_time_set", self._on_total_time_set)
        event_bus.subscribe("scenario_repeated", self._on_scenario_repeated)

    def _on_total_time_set(self, data=None):
        """Update UI when total time is set."""
        if data:
            time_limit = data['time_limit']
            self.status_display.add_message(f"⏰ Total time set: {time_limit:.2f} minutes", "info")
            self.status_bar.config(text=f"Time limit: {time_limit:.1f} minutes")

    def _on_scenario_repeated(self, data=None):
        """Update UI when scenario is repeated."""
        if data:
            file = data['file']
            time_remaining = data['time_remaining']
            self.status_display.add_message(f"🔁 Repeating scenario: {file} ({time_remaining:.1f}m remaining)", "success")

    def _on_command_started(self, data=None):
        """Update UI when a command starts."""
        if data:
            command = data['command']
            number = data['number']
            total = data['total']
            time_remaining = data.get('time_remaining', 'N/A')
            progress = data.get('progress', 0)
            
            status_text = f"Executing {command}... ({number}/{total})"
            if time_remaining != 'N/A':
                status_text += f" | Time: {time_remaining:.1f}m | Progress: {progress:.1f}%"
            
            self.status_display.add_message(f"🔄 {status_text}", "info")
            self.status_bar.config(text=status_text)

    def _on_command_executed(self, data=None):
        """Update UI when a command is executed."""
        if data:
            command = data['command']
            number = data['number']
            total = data['total']
            time_remaining = data.get('time_remaining', 'N/A')
            
            status_text = f"✅ Executed {command} ({number}/{total})"
            if time_remaining != 'N/A':
                status_text += f" | Time left: {time_remaining:.1f}m"
            
            self.status_display.add_message(status_text, "command")

            
    def _on_command_started(self, data=None):
        """Update UI when a command starts."""
        if data:
            command = data['command']
            number = data['number']
            total = data['total']
            self.status_display.add_message(f"🔄 Executing {command} ({number}/{total})...", "info")
            self.status_bar.config(text=f"Executing {command}... ({number}/{total})")

    def _on_scenario_loaded(self, data=None):
        """Update UI when scenario is loaded."""
        if data:
            file = data['file']
            count = data['command_count']
            self.status_display.add_message(f"📁 Loaded scenario: {file} ({count} commands)", "success")

    def _on_scenario_completed(self, data=None):
        """Update UI when scenario completes."""
        if data:
            file = data['file']
            commands = data['commands_executed']
            self.status_display.add_message(f"✅ Scenario completed: {file} ({commands} commands executed)", "success")
            self.status_bar.config(text="Scenario completed!")

    def _on_automation_error(self, data=None):
        """Update UI when automation error occurs."""
        if data:
            self.status_display.add_message(f"❌ Error: {data}", "error")
            self.status_bar.config(text="Error occurred!")


def main():
    """Main entry point for the GUI application."""
    print("Starting HumanAutomation Professional...")
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()