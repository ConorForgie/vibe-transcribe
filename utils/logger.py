"""
Simple logging setup for Vibe Transcribe
"""
import logging
from pathlib import Path
from typing import Optional


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO):
    """Set up logging configuration using basicConfig"""
    
    # Prepare basicConfig arguments
    config = {
        'level': level,
        'format': '%(message)s'
    }
    
    # If file logging is requested, set up filename
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            config['filename'] = log_file
            config['format'] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            config['datefmt'] = '%Y-%m-%d %H:%M:%S'
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")
            # Fall back to console only
    
    logging.basicConfig(**config)