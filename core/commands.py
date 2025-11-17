"""
Command pattern implementation - each action is a separate class.
This makes it easy to add new commands without changing existing code.
"""
import pyautogui
import random
import time
import subprocess
import winsound
from abc import ABC, abstractmethod
from typing import Dict, Any


class Command(ABC):
    """
    Base class for all commands.
    Think of commands as little workers that each know how to do one specific job.
    """
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]):
        """Every command must implement this method."""
        pass
    
    def random_delay(self, min_ms: int, max_ms: int):
        """Helper method for realistic delays between actions."""
        delay = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
        time.sleep(delay)
        return delay


class ClickCommand(Command):
    """Handles clicking on screen components."""
    
    def execute(self, params: Dict[str, Any]):
        component_id = params['target']
        delays = params.get('delays', {'min': 500, 'max': 1500})
        
        print(f"🖱️  Clicking on: {component_id}")
        
        # In a real implementation, this would use your component mapping
        # For now, we'll just simulate the click
        x, y = pyautogui.position()  # In real code, get from your component mapping
        pyautogui.click(x, y)
        
        # Add realistic delay
        delay = self.random_delay(delays['min'], delays['max'])
        print(f"⏰ Waited {delay:.2f}s after click")


class TypeCommand(Command):
    """Handles typing text."""
    
    def execute(self, params: Dict[str, Any]):
        text = params['target']
        delays = params.get('delays', {'min': 50, 'max': 150})
        
        print(f"⌨️  Typing: {text}")
        
        # Type each character with random delays (like a human)
        for char in text:
            pyautogui.typewrite(char)
            self.random_delay(delays['min'], delays['max'])
        
        print("✅ Finished typing")


class WaitCommand(Command):
    """Handles waiting for specified time."""
    
    def execute(self, params: Dict[str, Any]):
        min_minutes = params['min_value']
        max_minutes = params['max_value']
        
        wait_seconds = random.uniform(min_minutes * 60, max_minutes * 60)
        print(f"⏳ Waiting for {wait_seconds/60:.2f} minutes...")
        
        # Simple wait implementation (you can add your progress bar here)
        time.sleep(wait_seconds)
        print("✅ Wait completed")


class MoveMouseCommand(Command):
    """Moves mouse to random position."""
    
    def execute(self, params: Dict[str, Any]):
        print("🐭 Moving mouse randomly")
        
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        
        # Move to random position
        x = random.randint(100, screen_width - 100)
        y = random.randint(100, screen_height - 100)
        
        pyautogui.moveTo(x, y, duration=random.uniform(0.5, 2.0))
        print(f"📍 Mouse moved to ({x}, {y})")


class BeepCommand(Command):
    """Makes a beep sound."""
    
    def execute(self, params: Dict[str, Any]):
        delays = params.get('delays', {'min': 100, 'max': 1000})
        duration = random.randint(delays['min'], delays['max'])
        
        print(f"🔊 Beeping for {duration}ms")
        frequency = 2500  # High pitch
        winsound.Beep(frequency, duration)


class CommandFactory:
    """
    Factory class that creates command objects.
    This is like a command store - you ask for a command by name, and it gives you the right one.
    """
    
    # Dictionary mapping command names to command classes
    _command_classes = {
        'click': ClickCommand,
        'type': TypeCommand,
        'wait': WaitCommand,
        'movemouse': MoveMouseCommand,
        'beep': BeepCommand,
        # You can add more commands here easily!
    }
    
    @classmethod
    def create_command(cls, command_name: str) -> Command:
        """Create a command object by name."""
        command_name = command_name.lower()
        
        if command_name not in cls._command_classes:
            raise ValueError(f"Unknown command: {command_name}")
        
        return cls._command_classes[command_name]()
    
    @classmethod
    def register_command(cls, name: str, command_class):
        """Add a new command type to the factory."""
        cls._command_classes[name.lower()] = command_class
        print(f"✅ Registered new command: {name}")


# Example of how to add a new command:
class ExampleNewCommand(Command):
    """Example of how to add a new command."""
    
    def execute(self, params: Dict[str, Any]):
        print("🎉 This is a new command!")

# Register it: CommandFactory.register_command('example', ExampleNewCommand)