"""
Complete command implementation for HumanAutomation with proper error handling and logging.
"""
import pyautogui
import random
import time
import subprocess
import winsound
import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from .scenario_parser import ScenarioParser
from .scenario_resolver import ScenarioResolver
from .component_manager import ComponentManager
from .logger import automation_logger
from config import app_config


class Command(ABC):
    """
    Abstract base class for all automation commands.
    Provides common functionality for interruption handling and delays.
    """
    
    @abstractmethod
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        """Execute the command with given parameters and application state."""
        pass
    
    def random_delay(self, min_ms: int, max_ms: int, app_state=None) -> bool:
        """
        Perform a random delay with interruption support.
        Returns True if completed normally, False if interrupted.
        """
        delay_seconds = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
        return self.interruptible_sleep(delay_seconds, app_state)
    
    def interruptible_sleep(self, seconds: float, app_state=None) -> bool:
        """
        Sleep for specified seconds while checking for interruptions.
        Returns True if completed normally, False if interrupted.
        """
        if app_state is None:
            time.sleep(seconds)
            return True
        
        check_interval = 0.1  # Check every 100ms
        elapsed = 0.0
        
        while elapsed < seconds:
            # Check for stop conditions
            if not app_state.is_running or app_state.emergency_stop:
                return False
            
            # Handle pause state
            if app_state.is_paused:
                time.sleep(0.1)
                continue
            
            # Calculate sleep time for this iteration
            remaining = seconds - elapsed
            sleep_time = min(check_interval, remaining)
            time.sleep(sleep_time)
            elapsed += sleep_time
        
        return True


class ClickCommand(Command):
    """Handles clicking on mapped screen components."""
    
    def __init__(self):
        self.component_manager = ComponentManager(app_config)
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        component_id = params['target']
        delays = params.get('delays', {'min': 500, 'max': 1500})
        
        try:
            # Get component position for logging
            position = self.component_manager.get_component_position(component_id)
            
            # Perform the click
            success = self.component_manager.click_component(component_id)
            
            if success and position:
                x, y = position
                automation_logger.log_click(component_id, x, y)
            
            # Add post-click delay if not interrupted
            if success:
                if not self.random_delay(delays['min'], delays['max'], app_state):
                    automation_logger.log_info("Click delay interrupted")
            else:
                automation_logger.log_error(f"Failed to click component: {component_id}")
                
        except Exception as e:
            automation_logger.log_error(f"Error in click command for {component_id}: {e}")
            raise


class TypeCommand(Command):
    """Handles human-like text typing with random delays between characters."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        text = params['target']
        delays = params.get('delays', {'min': 50, 'max': 150})
        
        try:
            automation_logger.log_type(text)
            
            # Type each character with human-like random delays
            for char in text:
                # Check for interruption before each character
                if app_state and (not app_state.is_running or app_state.emergency_stop):
                    automation_logger.log_info("Typing interrupted")
                    break
                
                pyautogui.typewrite(char)
                
                # Delay between characters (can be interrupted)
                if not self.random_delay(delays['min'], delays['max'], app_state):
                    automation_logger.log_info("Typing delay interrupted")
                    break
                    
        except Exception as e:
            automation_logger.log_error(f"Error in type command for text '{text}': {e}")
            raise


class WaitCommand(Command):
    """Handles waiting for random time periods with interruption support."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        min_minutes = params['min_value']
        max_minutes = params['max_value']
        
        try:
            # Calculate random wait time
            wait_seconds = random.uniform(min_minutes * 60, max_minutes * 60)
            automation_logger.log_wait(wait_seconds / 60, wait_seconds)
            
            # Perform interruptible wait
            if not self.interruptible_sleep(wait_seconds, app_state):
                automation_logger.log_info("Wait command interrupted")
                
        except Exception as e:
            automation_logger.log_error(f"Error in wait command: {e}")
            raise


class MoveMouseCommand(Command):
    """Moves mouse to random screen position with human-like motion."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        try:
            # Get screen dimensions
            screen_width, screen_height = pyautogui.size()
            
            # Generate random position (avoiding edges)
            margin = 100
            x = random.randint(margin, screen_width - margin)
            y = random.randint(margin, screen_height - margin)
            
            # Move with human-like duration
            duration = random.uniform(0.5, 2.0)
            pyautogui.moveTo(x, y, duration=duration)
            
            automation_logger.log_mouse_move(x, y)
            
            # Brief delay after movement
            self.random_delay(200, 500, app_state)
            
        except Exception as e:
            automation_logger.log_error(f"Error in move mouse command: {e}")
            raise


class BeepCommand(Command):
    """Produces audible beep sound for user feedback."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        delays = params.get('delays', {'min': 100, 'max': 1000})
        
        try:
            duration = random.randint(delays['min'], delays['max'])
            frequency = 2500  # Hz
            
            automation_logger.log_beep(duration)
            winsound.Beep(frequency, duration)
            
        except Exception as e:
            automation_logger.log_error(f"Error in beep command: {e}")
            # Non-critical error, don't raise


class PressKeyCommand(Command):
    """Presses specified keyboard keys."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        key = params['target']
        delays = params.get('delays', {'min': 100, 'max': 500})
        
        try:
            automation_logger.log_info(f"KEYPRESS: {key}")
            pyautogui.press(key)
            
            # Post-keypress delay
            self.random_delay(delays['min'], delays['max'], app_state)
            
        except Exception as e:
            automation_logger.log_error(f"Error pressing key '{key}': {e}")
            raise


class TotalTimeCommand(Command):
    """Sets total execution time limit (handled by application)."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        min_total = params['min_value']
        max_total = params['max_value']
        
        automation_logger.log_info(f"TOTALTIME command received: {min_total}-{max_total} minutes")
        # Actual implementation handled in application loop


class CallCommand(Command):
    """Calls and executes another scenario file."""
    
    def __init__(self):
        self.resolver = ScenarioResolver(app_config)
        self.parser = ScenarioParser()
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        scenario_name = params['target']
        
        try:
            # Resolve scenario file path
            scenario_file = self.resolver.find_scenario_file(scenario_name)
            
            if not scenario_file or not os.path.exists(scenario_file):
                automation_logger.log_error(f"Scenario file not found: {scenario_name}")
                return
            
            automation_logger.log_scenario_call(scenario_name, scenario_file)
            
            # Parse and execute the called scenario
            commands = self.parser.read_scenario_file(scenario_file)
            
            if not commands:
                automation_logger.log_warning(f"No commands found in scenario: {scenario_file}")
                return
            
            automation_logger.log_info(f"Executing {len(commands)} commands from {scenario_name}")
            
            # Execute each command in the called scenario
            for i, command_data in enumerate(commands, 1):
                # Check for interruption before each command
                if app_state and (not app_state.is_running or app_state.emergency_stop):
                    automation_logger.log_info("Scenario call interrupted")
                    return
                
                command_name = command_data['type']
                
                try:
                    command = CommandFactory.create_command(command_name)
                    command.execute(command_data, app_state)
                    
                    # Check for interruption after command execution
                    if app_state and (not app_state.is_running or app_state.emergency_stop):
                        automation_logger.log_info("Scenario call interrupted during command execution")
                        return
                        
                except Exception as e:
                    automation_logger.log_error(f"Error executing command in called scenario: {e}")
                    # Continue with next command despite error
                    
        except Exception as e:
            automation_logger.log_error(f"Error in call command for {scenario_name}: {e}")
            raise


class ExecuteCommand(Command):
    """Executes external Python scripts with argument support."""
    
    def __init__(self):
        self.resolver = ScenarioResolver(app_config)
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        script_with_args = params['target']
        delays = params.get('delays', {'min': 500, 'max': 1500})
        
        try:
            # Parse script name and arguments
            parts = script_with_args.split()
            script_name = parts[0]
            script_args = parts[1:] if len(parts) > 1 else []
            
            # Find script file
            script_path = self._find_script_file(script_name)
            
            if not script_path or not os.path.exists(script_path):
                automation_logger.log_error(f"Script file not found: {script_name}")
                automation_logger.log_info("Searched in: executables/, tools/, scripts/")
                return
            
            automation_logger.log_script_execution(script_name, script_args, script_path)
            
            # Execute the script
            try:
                # Use current working directory as base
                cwd = os.getcwd()
                cmd = [sys.executable, script_path] + script_args
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    timeout=300  # 5-minute timeout
                )
                
                success = result.returncode == 0
                automation_logger.log_script_result(script_name, success, result.stdout)
                
                if not success:
                    if result.stderr:
                        automation_logger.log_error(f"Script stderr: {result.stderr.strip()}")
                    automation_logger.log_error(f"Script exit code: {result.returncode}")
                    
            except subprocess.TimeoutExpired:
                automation_logger.log_error(f"Script execution timed out: {script_name}")
            except Exception as e:
                automation_logger.log_error(f"Error executing script {script_name}: {e}")
            
            # Post-execution delay
            self.random_delay(delays['min'], delays['max'], app_state)
            
        except Exception as e:
            automation_logger.log_error(f"Error in execute command for {script_with_args}: {e}")
            raise
    
    def _find_script_file(self, script_name: str) -> Optional[str]:
        """Find script file in various locations."""
        # Check different possible locations - UPDATED to include scenarios/executables/
        possible_paths = [
            f"scenarios/executables/{script_name}",      # NEW: executables inside scenarios
            f"scenarios/executables/{script_name}.py",   # NEW: with .py extension
            f"executables/{script_name}",                # Keep original location
            f"executables/{script_name}.py",
            f"tools/{script_name}",
            f"tools/{script_name}.py",
            f"scripts/{script_name}",
            f"scripts/{script_name}.py",
            f"{script_name}",
            f"{script_name}.py"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None


class RepeatCommand(Command):
    """Signals intent to repeat scenario (handled by application)."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        automation_logger.log_info("REPEAT command received")
        # Actual repeat logic handled in application loop


class EndCommand(Command):
    """Ends scenario execution."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        automation_logger.log_info("END command received - stopping execution")
        if app_state:
            app_state.is_running = False


class ShutdownCommand(Command):
    """Placeholder for system shutdown command (disabled for safety)."""
    
    def execute(self, params: Dict[str, Any], app_state=None) -> None:
        automation_logger.log_warning("SHUTDOWN command detected - disabled for safety")
        automation_logger.log_info("In production, this would call system shutdown")


class CommandFactory:
    """
    Factory class for creating command instances.
    Implements singleton pattern for command instances.
    """
    
    _command_classes = {
        'click': ClickCommand,
        'type': TypeCommand,
        'wait': WaitCommand,
        'movemouse': MoveMouseCommand,
        'beep': BeepCommand,
        'press': PressKeyCommand,
        'totaltime': TotalTimeCommand,
        'call': CallCommand,
        'execute': ExecuteCommand,
        'repeat': RepeatCommand,
        'end': EndCommand,
        'shutdown': ShutdownCommand,
    }
    
    _instances = {}
    
    @classmethod
    def create_command(cls, command_name: str) -> Command:
        """Create or retrieve a command instance by name."""
        command_name = command_name.lower().strip()
        
        if command_name not in cls._command_classes:
            raise ValueError(f"Unknown command: '{command_name}'")
        
        # Use singleton pattern to avoid creating multiple instances
        if command_name not in cls._instances:
            cls._instances[command_name] = cls._command_classes[command_name]()
        
        return cls._instances[command_name]
    
    @classmethod
    def register_command(cls, name: str, command_class) -> None:
        """Register a new command type."""
        if not issubclass(command_class, Command):
            raise TypeError("Command class must inherit from Command base class")
        
        cls._command_classes[name.lower()] = command_class
        automation_logger.log_info(f"Registered new command: {name}")
    
    @classmethod
    def get_available_commands(cls) -> List[str]:
        """Get list of all available command names."""
        return list(cls._command_classes.keys())