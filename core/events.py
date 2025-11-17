"""
Simple event system for communication between components.
This is like a radio station - components can broadcast messages and others can listen.
"""
from typing import Dict, List, Callable, Any


class EventSystem:
    """
    Simple event system that lets different parts of our app talk to each other
    without knowing about each other directly.
    """
    
    def __init__(self):
        # Dictionary to store event listeners
        # Format: {"event_name": [list_of_functions_to_call]}
        self._listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_name: str, callback: Callable):
        """
        Subscribe to an event.
        When the event happens, the callback function will be called.
        """
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        
        self._listeners[event_name].append(callback)
        print(f"🎯 Subscribed to event: {event_name}")
    
    def publish(self, event_name: str, data: Any = None):
        """
        Publish an event - notify all subscribers.
        """
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"❌ Error in event handler for {event_name}: {e}")
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """Remove a subscription."""
        if event_name in self._listeners and callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)


# Create a global event system that everyone can use
event_bus = EventSystem()