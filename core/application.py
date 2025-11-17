"""
Complete application core for HumanAutomation with full time tracking and scenario management.
"""
import time
import threading
import random
from typing import Optional, Dict, Any, List
import os
from datetime import datetime

from .events import event_bus
from .scenario_parser import ScenarioParser
from .commands import CommandFactory
from .component_manager import ComponentManager
from .logger import automation_logger
from config import app_config


class AppState:
    """
    Thread-safe application state container.
    Tracks running, paused, and emergency stop states.
    """
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.emergency_stop = False
    
    def reset(self) -> None:
        """Reset state to initial values."""
        self.is_running = False
        self.is_paused = False
        self.emergency_stop = False


class TimeTracker:
    """
    Comprehensive time tracking for TOTALTIME and REPEAT functionality.
    Handles pauses and provides progress information.
    """
    
    def __init__(self):
        self.iteration_time_limit: float = 0.0  # in minutes
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0.0  # in minutes
        self.pause_start_time: Optional[float] = None
        self.total_pause_time: float = 0.0
        self.iteration_count: int = 0
    
    def start_iteration(self, time_limit_minutes: float) -> None:
        """Start tracking time for a new iteration."""
        self.iteration_time_limit = time_limit_minutes
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.total_pause_time = 0.0
        self.pause_start_time = None
        self.iteration_count += 1
        
        automation_logger.log_info(f"Time tracking started: {time_limit_minutes:.2f} minutes limit")
    
    def update_elapsed_time(self) -> float:
        """Update and return current elapsed time in minutes."""
        if self.start_time is None:
            return 0.0
        
        current_time = time.time()
        raw_elapsed = (current_time - self.start_time) / 60.0  # Convert to minutes
        
        # Subtract total pause time
        self.elapsed_time = raw_elapsed - self.total_pause_time
        return self.elapsed_time
    
    def get_remaining_time(self) -> float:
        """Get remaining time in minutes."""
        if self.iteration_time_limit == 0:
            return float('inf')
        
        self.update_elapsed_time()
        remaining = self.iteration_time_limit - self.elapsed_time
        return max(0.0, remaining)
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage (0-100)."""
        if self.iteration_time_limit == 0:
            return 0.0
        
        self.update_elapsed_time()
        if self.elapsed_time <= 0:
            return 0.0
        
        progress = (self.elapsed_time / self.iteration_time_limit) * 100.0
        return min(100.0, max(0.0, progress))
    
    def start_pause(self) -> None:
        """Record when pausing starts."""
        if self.pause_start_time is None and self.start_time is not None:
            self.pause_start_time = time.time()
    
    def end_pause(self) -> None:
        """Record when pausing ends and update total pause time."""
        if self.pause_start_time is not None:
            pause_duration = (time.time() - self.pause_start_time) / 60.0  # minutes
            self.total_pause_time += pause_duration
            self.pause_start_time = None
    
    def should_repeat(self) -> bool:
        """Check if there's enough time remaining to repeat."""
        remaining = self.get_remaining_time()
        return remaining > 2.0  # At least 2 minutes remaining to repeat
    
    def format_time_remaining(self) -> str:
        """Format remaining time as HH:MM:SS."""
        remaining_seconds = self.get_remaining_time() * 60.0
        hours = int(remaining_seconds // 3600)
        minutes = int((remaining_seconds % 3600) // 60)
        seconds = int(remaining_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_status_string(self) -> str:
        """Get formatted status string."""
        if self.iteration_time_limit == 0:
            return "No time limit set"
        
        progress = self.get_progress_percentage()
        remaining = self.format_time_remaining()
        return f"Progress: {progress:.1f}% | Remaining: {remaining} | Iteration: {self.iteration_count}"
    
    def reset(self) -> None:
        """Reset time tracker to initial state."""
        self.iteration_time_limit = 0.0
        self.start_time = None
        self.elapsed_time = 0.0
        self.total_pause_time = 0.0
        self.pause_start_time = None
        self.iteration_count = 0


class HumanAutomationApp:
    """
    Main application controller coordinating automation execution,
    time tracking, and scenario management.
    """
    
    def __init__(self):
        self.state = AppState()
        self.time_tracker = TimeTracker()
        self.scenario_parser = ScenarioParser()
        self.component_manager = ComponentManager(app_config)
        
        # Scenario execution state
        self.current_scenario: Optional[str] = None
        self.scenario_commands: List[Dict[str, Any]] = []
        self.original_scenario_commands: List[Dict[str, Any]] = []
        self.current_command_index: int = 0
        
        # Threading
        self.execution_thread: Optional[threading.Thread] = None
        self.thread_lock = threading.Lock()
        
        automation_logger.log_component_mapping(
            len(self.component_manager.components),
            app_config.delta_x,
            app_config.delta_y
        )
        automation_logger.log_info("HumanAutomation application initialized successfully")
    
    def load_scenario(self, scenario_file: str = None) -> bool:
        """
        Load and parse a scenario file.
        Uses config default if no file specified.
        """
        if scenario_file is None:
            scenario_file = app_config.main_scenario_file
        
        try:
            if not os.path.exists(scenario_file):
                automation_logger.log_error(f"Scenario file not found: {scenario_file}")
                event_bus.publish("scenario_error", {"file": scenario_file, "error": "File not found"})
                return False
            
            self.scenario_commands = self.scenario_parser.read_scenario_file(scenario_file)
            self.original_scenario_commands = self.scenario_commands.copy()
            self.current_scenario = scenario_file
            self.current_command_index = 0
            
            automation_logger.log_info(f"Loaded {len(self.scenario_commands)} commands from {scenario_file}")
            event_bus.publish("scenario_loaded", {
                "file": scenario_file,
                "command_count": len(self.scenario_commands),
                "commands": self.scenario_commands
            })
            return True
            
        except Exception as e:
            automation_logger.log_error(f"Error loading scenario {scenario_file}: {e}")
            event_bus.publish("scenario_error", {"file": scenario_file, "error": str(e)})
            return False
    
    def start_automation(self) -> bool:
        """Start the automation execution."""
        with self.thread_lock:
            if self.state.is_running:
                automation_logger.log_warning("Automation is already running")
                return False
            
            # Load scenario
            if not self.load_scenario():
                event_bus.publish("automation_error", "Failed to load scenario")
                return False
            
            if not self.scenario_commands:
                automation_logger.log_error("No commands found in scenario")
                event_bus.publish("automation_error", "No commands in scenario")
                return False
            
            # Reset state
            self.state.reset()
            self.time_tracker.reset()
            self.state.is_running = True
            self.current_command_index = 0
            
            # Log startup
            automation_logger.log_automation_start(self.current_scenario)
            
            # Start execution thread
            self.execution_thread = threading.Thread(
                target=self._run_scenario_loop,
                daemon=True,
                name="AutomationExecutor"
            )
            self.execution_thread.start()
            
            event_bus.publish("automation_started")
            automation_logger.log_info("Automation started successfully")
            return True
    
    def pause_automation(self) -> bool:
        """Pause or resume automation execution."""
        with self.thread_lock:
            if not self.state.is_running:
                automation_logger.log_warning("Cannot pause - automation is not running")
                return False
            
            self.state.is_paused = not self.state.is_paused
            
            if self.state.is_paused:
                self.time_tracker.start_pause()
                automation_logger.log_automation_pause()
                event_bus.publish("automation_paused")
            else:
                self.time_tracker.end_pause()
                automation_logger.log_automation_resume()
                event_bus.publish("automation_resumed")
            
            return True
    
    def stop_automation(self) -> bool:
        """Stop automation gracefully."""
        with self.thread_lock:
            if not self.state.is_running:
                automation_logger.log_warning("Automation is not running")
                return False
            
            self.state.is_running = False
            self.state.is_paused = False
            self.current_command_index = 0
            self.time_tracker.reset()
            
            automation_logger.log_automation_stop()
            event_bus.publish("automation_stopped")
            automation_logger.log_info("Automation stopped gracefully")
            return True
    
    def emergency_stop(self) -> bool:
        """Immediately stop all automation activities."""
        with self.thread_lock:
            automation_logger.log_emergency_stop()
            
            self.state.is_running = False
            self.state.is_paused = False
            self.state.emergency_stop = True
            self.current_command_index = 0
            self.time_tracker.reset()
            
            event_bus.publish("emergency_stop")
            automation_logger.log_info("Emergency stop activated")
            return True
    
    def set_total_time(self, min_minutes: float, max_minutes: float) -> None:
        """Set the total time limit for current iteration."""
        time_limit = random.uniform(min_minutes, max_minutes)
        self.time_tracker.start_iteration(time_limit)
        
        automation_logger.log_time_set(min_minutes, max_minutes, time_limit)
        
        event_bus.publish("total_time_set", {
            "time_limit": time_limit,
            "min_minutes": min_minutes,
            "max_minutes": max_minutes,
            "status": self.time_tracker.get_status_string()
        })
    
    def _check_repeat_condition(self) -> bool:
        """Check if scenario should be repeated based on time remaining."""
        if self.time_tracker.iteration_time_limit == 0:
            return False
        
        remaining = self.time_tracker.get_remaining_time()
        should_repeat = self.time_tracker.should_repeat()
        
        automation_logger.log_repeat_check(remaining, should_repeat)
        return should_repeat
    
    def _repeat_scenario(self) -> None:
        """Repeat the current scenario from the beginning."""
        automation_logger.log_info("Repeating scenario")
        
        self.current_command_index = 0
        self.scenario_commands = self.original_scenario_commands.copy()
        
        # Click last Chrome tab before repeating
        self.component_manager.click_last_chrome_tab()
        
        event_bus.publish("scenario_repeated", {
            "file": self.current_scenario,
            "time_remaining": self.time_tracker.get_remaining_time(),
            "iteration": self.time_tracker.iteration_count
        })
    
    def _execute_command(self, command_data: Dict[str, Any], command_index: int, total_commands: int) -> bool:
        """
        Execute a single command with proper error handling and logging.
        Returns True if execution should continue, False if should stop.
        """
        command_name = command_data['type']
        
        try:
            # Log command start
            automation_logger.log_command_start(command_name, command_data, command_index, total_commands)
            
            # Publish command start event
            event_bus.publish("command_started", {
                'command': command_name,
                'number': command_index,
                'total': total_commands,
                'data': command_data,
                'time_remaining': self.time_tracker.get_remaining_time(),
                'progress': self.time_tracker.get_progress_percentage(),
                'status': self.time_tracker.get_status_string()
            })
            
            # Handle special commands
            if command_name == 'totaltime':
                min_time = command_data['min_value']
                max_time = command_data['max_value']
                self.set_total_time(min_time, max_time)
                return True
            
            if command_name == 'repeat':
                if self._check_repeat_condition():
                    self._repeat_scenario()
                    return False  # Stop current execution to restart
                else:
                    return True
            
            # Execute normal command
            command = CommandFactory.create_command(command_name)
            command.execute(command_data, self.state)
            
            # Check for interruption after command execution
            if not self.state.is_running or self.state.emergency_stop:
                return False
            
            # Log command completion
            automation_logger.log_command_complete(command_name, command_index, total_commands)
            
            # Publish command completion event
            event_bus.publish("command_executed", {
                'command': command_name,
                'number': command_index,
                'total': total_commands,
                'data': command_data,
                'time_remaining': self.time_tracker.get_remaining_time(),
                'progress': self.time_tracker.get_progress_percentage(),
                'status': self.time_tracker.get_status_string()
            })
            
            return True
            
        except Exception as e:
            automation_logger.log_command_error(command_name, str(e), command_index, total_commands)
            event_bus.publish("command_error", {
                'command': command_data,
                'error': str(e),
                'number': command_index,
                'total': total_commands
            })
            return True  # Continue despite error
    
    def _run_scenario_loop(self) -> None:
        """
        Main scenario execution loop.
        Handles command execution, time tracking, and repetition.
        """
        automation_logger.log_info("Starting scenario execution loop")
        
        # Click last Chrome tab before starting
        self.component_manager.click_last_chrome_tab()
        
        try:
            while self.state.is_running and not self.state.emergency_stop:
                total_commands = len(self.scenario_commands)
                
                # Execute commands in current scenario
                while (self.state.is_running and 
                       not self.state.emergency_stop and
                       self.current_command_index < total_commands):
                    
                    # Handle pause state
                    if self.state.is_paused:
                        time.sleep(0.5)
                        continue
                    
                    # Check time limit
                    if (self.time_tracker.iteration_time_limit > 0 and 
                        self.time_tracker.get_remaining_time() <= 0):
                        automation_logger.log_info("Time limit reached - stopping execution")
                        break
                    
                    # Execute current command
                    command_data = self.scenario_commands[self.current_command_index]
                    should_continue = self._execute_command(
                        command_data, 
                        self.current_command_index + 1, 
                        total_commands
                    )
                    
                    if not should_continue:
                        break
                    
                    self.current_command_index += 1
                    
                    # Brief delay between commands (unless it's a wait command)
                    if command_data['type'] != 'wait' and self.state.is_running:
                        time.sleep(0.1)
                
                # Check if we should repeat the scenario
                if (self.state.is_running and 
                    not self.state.emergency_stop and
                    self.current_command_index >= total_commands and
                    self._check_repeat_condition()):
                    
                    self._repeat_scenario()
                else:
                    break  # Exit main loop
                    
        except Exception as e:
            automation_logger.log_error(f"Critical error in scenario loop: {e}")
        
        # Final state update and cleanup
        finally:
            if self.current_command_index >= len(self.scenario_commands) and self.state.is_running:
                automation_logger.log_info("Scenario completed successfully")
                event_bus.publish("scenario_completed", {
                    "file": self.current_scenario,
                    "commands_executed": len(self.scenario_commands),
                    "total_time_used": self.time_tracker.elapsed_time,
                    "iterations": self.time_tracker.iteration_count
                })
            else:
                automation_logger.log_info("Scenario execution interrupted or stopped")
            
            self.state.is_running = False
            self.state.emergency_stop = False
            automation_logger.log_automation_stop()
            event_bus.publish("automation_stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status."""
        return {
            "is_running": self.state.is_running,
            "is_paused": self.state.is_paused,
            "emergency_stop": self.state.emergency_stop,
            "current_scenario": self.current_scenario,
            "current_command": self.current_command_index,
            "total_commands": len(self.scenario_commands),
            "time_remaining": self.time_tracker.get_remaining_time(),
            "progress": self.time_tracker.get_progress_percentage(),
            "status_string": self.time_tracker.get_status_string(),
            "iteration": self.time_tracker.iteration_count
        }