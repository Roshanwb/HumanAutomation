"""
Main application class that coordinates everything.
This is the brain of our automation system.
"""
import time
import threading
from typing import Optional

from config import app_config
from .events import event_bus
from .commands import CommandFactory, Command
from .scenario_parser import ScenarioParser


class HumanAutomationApp:
    """
    Main application class that ties everything together.
    Follows the Facade pattern - provides a simple interface to complex system.
    """
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.current_scenario = None
        
        # Load configuration
        app_config.load_from_file()
        app_config.ensure_directories()
        
        # Set up event listeners
        self._setup_event_handlers()
        
        print("🚀 HumanAutomation App initialized!")
    
    def _setup_event_handlers(self):
        """Set up listeners for various events."""
        event_bus.subscribe("automation_started", self._on_automation_started)
        event_bus.subscribe("automation_stopped", self._on_automation_stopped)
        event_bus.subscribe("automation_paused", self._on_automation_paused)
    
    def start_automation(self):
        """Start the main automation loop."""
        if self.is_running:
            print("⚠️  Automation is already running")
            return
        
        self.is_running = True
        self.is_paused = False
        
        # Start automation in a separate thread so the UI doesn't freeze
        thread = threading.Thread(target=self._run_automation_loop, daemon=True)
        thread.start()
        
        event_bus.publish("automation_started")
        print("✅ Automation started!")
    
    def pause_automation(self):
        """Pause or resume automation."""
        if not self.is_running:
            print("⚠️  Automation is not running")
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            event_bus.publish("automation_paused")
            print("⏸️  Automation paused")
        else:
            event_bus.publish("automation_resumed")
            print("▶️  Automation resumed")
    
    def stop_automation(self):
        """Stop automation gracefully."""
        self.is_running = False
        self.is_paused = False
        event_bus.publish("automation_stopped")
        print("🛑 Automation stopped")
    
    def emergency_stop(self):
        """Immediately stop all automation."""
        print("🚨 EMERGENCY STOP!")
        self.is_running = False
        self.is_paused = False
        event_bus.publish("emergency_stop")
    
    def _run_automation_loop(self):
        """Main automation loop - runs in background thread."""
        print("🔄 Starting automation loop...")
        
        while self.is_running:
            if self.is_paused:
                # If paused, just wait and check again
                time.sleep(0.5)
                continue
            
            try:
                # Execute the main scenario
                self._execute_scenario(app_config.main_scenario_file)
                
                # Small delay between scenario executions
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in automation loop: {e}")
                event_bus.publish("automation_error", e)
                break
        
        print("🔚 Automation loop ended")
    
    def _execute_scenario(self, scenario_file: str):
        """Execute a scenario file."""
        print(f"📋 Executing scenario: {scenario_file}")
        
        # Parse the scenario file into commands
        commands = ScenarioParser.read_scenario_file(scenario_file)
        
        if not commands:
            print(f"⚠️  No commands found in {scenario_file}")
            return
        
        # Execute each command
        for i, command_data in enumerate(commands, 1):
            if not self.is_running:
                break
            if self.is_paused:
                # Wait while paused
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                if not self.is_running:
                    break
            
            try:
                print(f"🔧 Executing command {i}/{len(commands)}: {command_data['type']}")
                
                # Create and execute the command
                command = CommandFactory.create_command(command_data['type'])
                command.execute(command_data)
                
                event_bus.publish("command_executed", {
                    'command': command_data['type'],
                    'number': i,
                    'total': len(commands)
                })
                
            except Exception as e:
                print(f"❌ Error executing command {command_data}: {e}")
                event_bus.publish("command_error", {
                    'command': command_data,
                    'error': e
                })
    
    def _on_automation_started(self, data=None):
        print("🎉 Automation started event received!")
    
    def _on_automation_stopped(self, data=None):
        print("🛑 Automation stopped event received!")
    
    def _on_automation_paused(self, data=None):
        print("⏸️  Automation paused event received!")