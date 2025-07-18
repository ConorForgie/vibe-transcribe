"""
Global hotkey handling using keyboard library
"""
import asyncio
import logging
import threading
from typing import Dict, Callable, Optional
import keyboard


class HotkeyManager:
    def __init__(self, hotkey_config: Dict[str, str]):
        self.hotkey_config = hotkey_config
        self.logger = logging.getLogger(__name__)
        
        self.toggle_callback: Optional[Callable] = None
        self.hold_start_callback: Optional[Callable] = None
        self.hold_end_callback: Optional[Callable] = None
        
        self.hold_key_pressed = False
        self.hotkeys_registered = False
        
    def set_callbacks(self, toggle_callback: Callable = None, 
                     hold_start_callback: Callable = None,
                     hold_end_callback: Callable = None):
        """Set the callback functions for hotkey events"""
        self.toggle_callback = toggle_callback
        self.hold_start_callback = hold_start_callback
        self.hold_end_callback = hold_end_callback
        
    def _run_async_callback(self, callback):
        """Run an async callback in a new thread"""
        def run_callback():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(callback())
            loop.close()
            
        threading.Thread(target=run_callback, daemon=True).start()
        
    def _on_toggle_hotkey(self):
        """Handle toggle hotkey"""
        self.logger.info("🔄 Toggle hotkey detected!")
        if self.toggle_callback:
            self._run_async_callback(self.toggle_callback)
            
    def _on_hold_press(self):
        """Handle hold hotkey press"""
        if not self.hold_key_pressed:
            self.hold_key_pressed = True
            self.logger.info("🎤 Hold hotkey start detected!")
            if self.hold_start_callback:
                self._run_async_callback(self.hold_start_callback)
                
    def _on_hold_release(self):
        """Handle hold hotkey release"""
        if self.hold_key_pressed:
            self.hold_key_pressed = False
            self.logger.info("🛑 Hold hotkey end detected!")
            if self.hold_end_callback:
                self._run_async_callback(self.hold_end_callback)
        
    def start(self):
        """Start listening for hotkeys"""
        try:
            # Register toggle hotkey
            keyboard.add_hotkey(
                self.hotkey_config["toggle"], 
                self._on_toggle_hotkey
            )
            
            # Register hold hotkey (press and release)
            keyboard.on_press_key(
                self.hotkey_config["hold"], 
                lambda _: self._on_hold_press()
            )
            keyboard.on_release_key(
                self.hotkey_config["hold"], 
                lambda _: self._on_hold_release()
            )
            
            self.hotkeys_registered = True
            self.logger.info(f"Hotkey listener started with toggle: {self.hotkey_config['toggle']}, hold: {self.hotkey_config['hold']}")
            
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}")
            self.logger.error("Another application may be using these hotkey combinations")
            raise
            
    def stop(self):
        """Stop listening for hotkeys"""
        if self.hotkeys_registered:
            try:
                keyboard.clear_all_hotkeys()
                keyboard.unhook_all()
                self.hotkeys_registered = False
                self.logger.info("Hotkey listener stopped")
            except Exception as e:
                self.logger.warning(f"Error stopping hotkey listener: {e}")