"""
Clipboard operations with console fallback
"""
import logging
import pyperclip
from typing import Optional


class ClipboardManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard, return True if successful"""
        try:
            pyperclip.copy(text)
            
            # Verify the copy worked by reading it back
            copied_text = pyperclip.paste()
            if copied_text == text:
                return True
            else:
                self.logger.warning("Clipboard copy verification failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to copy to clipboard: {e}")
            return False
            
    def get_from_clipboard(self) -> Optional[str]:
        """Get text from clipboard"""
        try:
            return pyperclip.paste()
        except Exception as e:
            self.logger.error(f"Failed to read from clipboard: {e}")
            return None
            
    def test_clipboard(self) -> bool:
        """Test clipboard functionality"""
        test_text = "vibe-transcribe-test"
        
        try:
            # Save current clipboard content
            original_content = self.get_from_clipboard()
            
            # Test copy/paste
            success = self.copy_to_clipboard(test_text)
            if success:
                retrieved = self.get_from_clipboard()
                if retrieved == test_text:
                    self.logger.info("Clipboard test successful")
                    
                    # Restore original content if possible
                    if original_content is not None:
                        self.copy_to_clipboard(original_content)
                        
                    return True
                    
            self.logger.error("Clipboard test failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Clipboard test error: {e}")
            return False