"""
Audio recording functionality using soundcard library
"""
import logging
import numpy as np
import soundcard as sc
from typing import Optional, Dict, Any
import threading
import time


class AudioRecorder:
    def __init__(self, audio_config: Dict[str, Any]):
        self.sample_rate = audio_config["sample_rate"]
        self.channels = audio_config["channels"] 
        self.dtype = audio_config["dtype"]
        self.max_duration = audio_config.get("max_duration", 300)
        self.logger = logging.getLogger(__name__)
        
        self.is_recording = False
        self.audio_data = []
        self.recording_thread = None
        self.start_time = None
        
        # Get default microphone
        try:
            self.microphone = sc.default_microphone()
            if self.microphone:
                self.logger.debug(f"Using microphone: {self.microphone}")
            else:
                self.logger.warning("No default microphone found")
        except Exception as e:
            self.logger.error(f"Error getting default microphone: {e}")
            self.microphone = None
        
    def start_recording(self):
        """Start recording audio to memory"""
        if self.is_recording:
            self.logger.warning("Already recording")
            return
            
        if not self.microphone:
            raise RuntimeError("No microphone available")
            
        self.is_recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        def record_worker():
            """Worker thread for recording"""
            try:
                # Record in chunks of 1 second
                chunk_size = self.sample_rate  # 1 second of samples
                
                while self.is_recording:
                    # Check for timeout
                    if time.time() - self.start_time > self.max_duration:
                        self.logger.warning(f"Recording stopped: exceeded max duration of {self.max_duration}s")
                        break
                        
                    # Record chunk
                    chunk = self.microphone.record(
                        samplerate=self.sample_rate,
                        numframes=chunk_size,
                        channels=self.channels
                    )
                    
                    if self.is_recording:  # Check again in case we were stopped
                        self.audio_data.append(chunk)
                        
            except Exception as e:
                self.logger.error(f"Recording error: {e}")
            finally:
                self.is_recording = False
                
        self.recording_thread = threading.Thread(target=record_worker, daemon=True)
        self.recording_thread.start()
            
    def stop_recording(self) -> Optional[np.ndarray]:
        """Stop recording and return audio data"""
        if not self.is_recording:
            self.logger.warning("Not currently recording")
            return None
            
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)
            
        if not self.audio_data:
            return None
            
        # Concatenate all recorded chunks
        try:
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Convert to mono if needed (take first channel)
            if len(audio_array.shape) > 1 and audio_array.shape[1] > 1:
                audio_array = audio_array[:, 0]
            
            # Ensure it's a 1D array
            if len(audio_array.shape) > 1:
                audio_array = audio_array.squeeze()
                
            return audio_array.astype(np.float32)
            
        except Exception as e:
            self.logger.error(f"Error processing audio data: {e}")
            return None
        
    def get_available_devices(self):
        """Get list of available audio devices"""
        try:
            mics = sc.all_microphones()
            speakers = sc.all_speakers()
            return {
                "microphones": [str(mic) for mic in mics],
                "speakers": [str(speaker) for speaker in speakers]
            }
        except Exception as e:
            self.logger.error(f"Error getting devices: {e}")
            return {"microphones": [], "speakers": []}