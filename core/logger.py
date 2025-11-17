"""
Professional logging system for HumanAutomation.
Creates timestamped log files and records all actions.
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from config import app_config


class AutomationLogger:
    """
    Comprehensive logging system that creates timestamped log files
    and records all automation activities with proper error handling.
    """
    
    def __init__(self):
        self.log_dir = app_config.log_dir
        self.current_log_file: Optional[str] = None
        self.logger: Optional[logging.Logger] = None
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging with timestamped file and console output."""
        try:
            # Create log directory if it doesn't exist
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Create timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_log_file = os.path.join(self.log_dir, f"automation_{timestamp}.log")
            
            # Configure logging
            self.logger = logging.getLogger('HumanAutomation')
            self.logger.setLevel(logging.INFO)
            
            # Clear any existing handlers to avoid duplicates
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            
            # File handler
            file_handler = logging.FileHandler(self.current_log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
            # Log startup information
            self.logger.info("=" * 60)
            self.logger.info("🤖 HumanAutomation Professional - Session Started")
            self.logger.info("=" * 60)
            self.logger.info(f"Log file: {self.current_log_file}")
            self.logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ CRITICAL: Failed to setup logging: {e}")
            raise
    
    def log_automation_start(self, scenario_file: str) -> None:
        """Log automation start."""
        self._safe_log_info(f"🚀 AUTOMATION STARTED")
        self._safe_log_info(f"📁 Scenario: {scenario_file}")
        self._safe_log_info("-" * 50)
    
    def log_automation_stop(self) -> None:
        """Log automation stop."""
        self._safe_log_info("-" * 50)
        self._safe_log_info("🛑 AUTOMATION STOPPED")
    
    def log_automation_pause(self) -> None:
        """Log automation pause."""
        self._safe_log_info("⏸️  AUTOMATION PAUSED")
    
    def log_automation_resume(self) -> None:
        """Log automation resume."""
        self._safe_log_info("▶️  AUTOMATION RESUMED")
    
    def log_emergency_stop(self) -> None:
        """Log emergency stop."""
        self._safe_log_info("🚨 EMERGENCY STOP ACTIVATED")
    
    def log_command_start(self, command_type: str, command_data: Dict[str, Any], index: int, total: int) -> None:
        """Log command execution start."""
        self._safe_log_info(f"🔧 Command {index}/{total}: {command_type.upper()}")
        if command_data:
            self._safe_log_info(f"   📋 Parameters: {command_data}")
    
    def log_command_complete(self, command_type: str, index: int, total: int) -> None:
        """Log command completion."""
        self._safe_log_info(f"   ✅ Completed: {command_type.upper()}")
    
    def log_command_error(self, command_type: str, error: str, index: int, total: int) -> None:
        """Log command error."""
        self._safe_log_error(f"   ❌ Error in {command_type.upper()}: {error}")
    
    def log_click(self, component_id: str, x: int, y: int) -> None:
        """Log component click."""
        self._safe_log_info(f"🖱️  CLICK: {component_id} at ({x}, {y})")
    
    def log_type(self, text: str) -> None:
        """Log text typing."""
        # Mask passwords or sensitive data
        if any(keyword in text.lower() for keyword in ['password', 'pwd', 'secret']):
            masked_text = '*' * len(text)
            self._safe_log_info(f"⌨️  TYPE: {masked_text} [MASKED]")
        else:
            self._safe_log_info(f"⌨️  TYPE: '{text}'")
    
    def log_wait(self, minutes: float, seconds: float) -> None:
        """Log wait command."""
        self._safe_log_info(f"⏳ WAIT: {minutes:.2f} minutes ({seconds:.0f} seconds)")
    
    def log_mouse_move(self, x: int, y: int) -> None:
        """Log mouse movement."""
        self._safe_log_info(f"🐭 MOVE: Mouse moved to ({x}, {y})")
    
    def log_beep(self, duration: int) -> None:
        """Log beep sound."""
        self._safe_log_info(f"🔊 BEEP: {duration}ms")
    
    def log_scenario_call(self, scenario_name: str, scenario_file: str) -> None:
        """Log scenario call."""
        self._safe_log_info(f"📞 CALL: {scenario_name} -> {scenario_file}")
    
    def log_script_execution(self, script_name: str, args: list, script_path: str) -> None:
        """Log script execution."""
        self._safe_log_info(f"🐍 EXECUTE: {script_name} with args {args}")
        self._safe_log_info(f"   📁 Script: {script_path}")
    
    def log_script_result(self, script_name: str, success: bool, output: str = "") -> None:
        """Log script execution result."""
        status = "SUCCESS" if success else "FAILED"
        self._safe_log_info(f"   📝 Script {status}: {script_name}")
        if output and success:
            # Limit output length to prevent log spam
            truncated_output = output[:500] + "..." if len(output) > 500 else output
            self._safe_log_info(f"   📋 Output: {truncated_output.strip()}")
    
    def log_time_set(self, min_minutes: float, max_minutes: float, actual_minutes: float) -> None:
        """Log total time setting."""
        self._safe_log_info(f"⏰ TOTALTIME: {min_minutes}-{max_minutes} minutes (set to {actual_minutes:.2f})")
    
    def log_repeat_check(self, remaining_time: float, should_repeat: bool) -> None:
        """Log repeat condition check."""
        action = "REPEATING" if should_repeat else "STOPPING"
        self._safe_log_info(f"🔁 REPEAT: {remaining_time:.2f}m remaining -> {action}")
    
    def log_component_mapping(self, component_count: int, delta_x: int, delta_y: int) -> None:
        """Log component mapping info."""
        self._safe_log_info(f"🗺️  MAPPING: Loaded {component_count} components (ΔX={delta_x}, ΔY={delta_y})")
    
    def log_chrome_tab(self, component_id: str) -> None:
        """Log Chrome tab update."""
        self._safe_log_info(f"📌 CHROME TAB: Set to {component_id}")
    
    def log_info(self, message: str) -> None:
        """Log general information."""
        self._safe_log_info(f"ℹ️  INFO: {message}")
    
    def log_warning(self, message: str) -> None:
        """Log warning."""
        self._safe_log_warning(f"⚠️  WARNING: {message}")
    
    def log_error(self, message: str) -> None:
        """Log error."""
        self._safe_log_error(f"❌ ERROR: {message}")
    
    def _safe_log_info(self, message: str) -> None:
        """Safely log info message with error handling."""
        try:
            if self.logger:
                self.logger.info(message)
            else:
                print(f"INFO: {message}")
        except Exception:
            print(f"INFO: {message}")
    
    def _safe_log_warning(self, message: str) -> None:
        """Safely log warning message with error handling."""
        try:
            if self.logger:
                self.logger.warning(message)
            else:
                print(f"WARNING: {message}")
        except Exception:
            print(f"WARNING: {message}")
    
    def _safe_log_error(self, message: str) -> None:
        """Safely log error message with error handling."""
        try:
            if self.logger:
                self.logger.error(message)
            else:
                print(f"ERROR: {message}")
        except Exception:
            print(f"ERROR: {message}")
    
    def get_log_file_path(self) -> str:
        """Get current log file path."""
        return self.current_log_file or ""


# Global logger instance
automation_logger = AutomationLogger()