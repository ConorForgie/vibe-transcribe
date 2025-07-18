"""
Global hotkey handling using pynput
"""
import asyncio
import logging
from typing import Dict, Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import threading


class HotkeyManager:
    def __init__(self, hotkey_config: Dict[str, str]):
        self.hotkey_config = hotkey_config
        self.logger = logging.getLogger(__name__)
        
        self.toggle_callback: Optional[Callable] = None
        self.hold_start_callback: Optional[Callable] = None
        self.hold_end_callback: Optional[Callable] = None
        
        self.listener = None
        self.currently_pressed = set()
        self.hold_key_pressed = False
        
        # Parse hotkey combinations
        self.toggle_keys = self._parse_hotkey(hotkey_config["toggle"])
        self.hold_keys = self._parse_hotkey(hotkey_config["hold"])
        
    def _parse_hotkey(self, hotkey_str: str) -> set:
        """Parse hotkey string into set of keys"""
        keys = set()
        parts = hotkey_str.lower().split('+')
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(Key.ctrl_l)
                keys.add(Key.ctrl_r)
            elif part == 'alt':
                keys.add(Key.alt_l) 
                keys.add(Key.alt_r)
            elif part == 'shift':
                keys.add(Key.shift_l)
                keys.add(Key.shift_r)
            elif part == 'cmd' or part == 'super':
                keys.add(Key.cmd)
            else:
                # Regular character key
                try:
                    keys.add(KeyCode.from_char(part))
                except:
                    self.logger.warning(f"Could not parse key: {part}")
                    
        return keys
        
    def _key_matches_combination(self, key_set: set) -> bool:
        """Check if currently pressed keys match the given combination"""
        # For modifier combinations, we need to check if all required keys are pressed
        required_keys = key_set.copy()
        pressed_keys = self.currently_pressed.copy()
        
        # Handle modifier key variants (left/right)
        for required_key in list(required_keys):
            if required_key in pressed_keys:
                continue
            elif hasattr(required_key, 'vk'):
                # Check if any pressed key matches this one
                for pressed_key in pressed_keys:
                    if hasattr(pressed_key, 'vk') and pressed_key.vk == required_key.vk:
                        break
                else:
                    return False
            else:
                return False
                
        return len(pressed_keys.intersection(required_keys)) > 0
        
    def _on_key_press(self, key):
        """Handle key press events"""
        self.currently_pressed.add(key)
        
        # Check for toggle hotkey
        if self._key_matches_combination(self.toggle_keys):
            if self.toggle_callback:
                # Run async callback in thread
                def run_callback():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.toggle_callback())
                    loop.close()
                    
                threading.Thread(target=run_callback, daemon=True).start()
                
        # Check for hold hotkey start
        elif self._key_matches_combination(self.hold_keys) and not self.hold_key_pressed:
            self.hold_key_pressed = True
            if self.hold_start_callback:
                def run_callback():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.hold_start_callback())
                    loop.close()
                    
                threading.Thread(target=run_callback, daemon=True).start()
                
    def _on_key_release(self, key):
        """Handle key release events"""
        self.currently_pressed.discard(key)
        
        # Check if hold hotkey was released
        if self.hold_key_pressed and not self._key_matches_combination(self.hold_keys):
            self.hold_key_pressed = False
            if self.hold_end_callback:
                def run_callback():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.hold_end_callback())
                    loop.close()
                    
                threading.Thread(target=run_callback, daemon=True).start()
                
    def set_callbacks(self, toggle_callback: Callable = None, 
                     hold_start_callback: Callable = None,
                     hold_end_callback: Callable = None):
        """Set the callback functions for hotkey events"""
        self.toggle_callback = toggle_callback
        self.hold_start_callback = hold_start_callback
        self.hold_end_callback = hold_end_callback
        
    def start(self):
        """Start listening for hotkeys"""
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            self.logger.info(f"Hotkey listener started with toggle: {self.hotkey_config['toggle']}, hold: {self.hotkey_config['hold']}")
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}")
            # Log if another app might be using the hotkeys
            self.logger.error("Another application may be using these hotkey combinations")
            raise
            
    def stop(self):
        """Stop listening for hotkeys"""
        if self.listener:
            self.listener.stop()
            self.logger.info("Hotkey listener stopped")