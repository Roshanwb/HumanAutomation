"""
Parses scenario files and converts them into commands.
Think of this as a recipe reader that understands your automation language.
"""
import re
from typing import Dict, Any, Optional, List


class ScenarioParser:
    """
    Reads scenario files and converts each line into command data.
    This understands the special syntax of your scenario files.
    """
    
    @staticmethod
    def parse_line(line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single line from a scenario file.
        Returns command data if the line is valid, None if it's a comment or empty.
        """
        line = line.strip()
        
        # Skip empty lines and comments (lines starting with #)
        if not line or line.startswith('#'):
            return None
        
        print(f"📖 Reading line: {line}")
        
        # Split command part and parameters part
        parts = line.split(',', 1)
        command_part = parts[0].strip()
        params_part = parts[1].strip() if len(parts) > 1 else ""
        
        # Figure out what type of command this is
        if command_part.lower().startswith(('click', 'type', 'press')):
            return ScenarioParser._parse_action_command(command_part, params_part)
        elif command_part.lower().startswith(('wait', 'totaltime')):
            return ScenarioParser._parse_timing_command(command_part, params_part)
        else:
            return ScenarioParser._parse_simple_command(command_part, params_part)
    
    @staticmethod
    def _parse_action_command(command: str, params: str) -> Dict[str, Any]:
        """Parse commands like 'click button1' or 'type "hello"'."""
        # Split the command into type and target
        # Example: "click button1" -> type="click", target="button1"
        command_parts = command.split(' ', 1)
        command_type = command_parts[0].lower()
        target = command_parts[1] if len(command_parts) > 1 else ""
        
        # Handle quoted text (for type commands)
        if '"' in target:
            # Extract text inside quotes
            target = target.split('"')[1]
        
        # Parse delay parameters (like "500-1500")
        delays = ScenarioParser._parse_delays(params)
        
        return {
            'type': command_type,
            'target': target,
            'delays': delays
        }
    
    @staticmethod
    def _parse_timing_command(command: str, params: str) -> Dict[str, Any]:
        """Parse timing commands like 'wait 1-5'."""
        # Split time range (like "1-5" -> min=1, max=5)
        if '-' in params:
            time_parts = params.split('-')
            min_time = float(time_parts[0])
            max_time = float(time_parts[1])
        else:
            min_time = max_time = float(params) if params else 0.1
        
        return {
            'type': command.lower(),
            'min_value': min_time,
            'max_value': max_time
        }
    
    @staticmethod
    def _parse_simple_command(command: str, params: str) -> Dict[str, Any]:
        """Parse simple commands without complex parameters."""
        return {
            'type': command.lower(),
            'params': params
        }
    
    @staticmethod
    def _parse_delays(param_string: str) -> Dict[str, int]:
        """Parse delay range like '500-1500' into min and max."""
        if not param_string:
            return {'min': 500, 'max': 1500}  # Default delays
        
        if '-' in param_string:
            min_delay, max_delay = map(int, param_string.split('-'))
            return {'min': min_delay, 'max': max_delay}
        else:
            delay = int(param_string)
            return {'min': delay, 'max': delay}
    
    @staticmethod
    def read_scenario_file(file_path: str) -> List[Dict[str, Any]]:
        """
        Read entire scenario file and return list of commands.
        """
        commands = []
        
        try:
            with open(file_path, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    command_data = ScenarioParser.parse_line(line)
                    if command_data:
                        commands.append(command_data)
            
            print(f"✅ Loaded {len(commands)} commands from {file_path}")
            return commands
            
        except FileNotFoundError:
            print(f"❌ Scenario file not found: {file_path}")
            return []
        except Exception as e:
            print(f"❌ Error reading scenario file: {e}")
            return []