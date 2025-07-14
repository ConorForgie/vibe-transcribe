"""
Faster-Whisper integration for speech-to-text transcription
"""
import logging
import numpy as np
from faster_whisper import WhisperModel
from typing import Dict, Any, Optional
import os


class WhisperClient:
    def __init__(self, whisper_config: Dict[str, Any]):
        self.model_name = whisper_config["model"]
        self.language = whisper_config.get("language")
        self.device = whisper_config.get("device", "cpu")
        self.logger = logging.getLogger(__name__)
        
        self.model: Optional[WhisperModel] = None
        self._model_loaded = False
        
    def _load_model(self):
        """Load the Whisper model (lazy loading)"""
        if self._model_loaded:
            return
            
        try:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            
            # Set up model cache directory
            cache_dir = os.path.expanduser("~/.cache/whisper")
            os.makedirs(cache_dir, exist_ok=True)
            
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                download_root=cache_dir
            )
            
            self._model_loaded = True
            self.logger.info(f"Whisper model loaded successfully on {self.device}")
            
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model {self.model_name}: {e}")
            
            # Try fallback to smaller model
            if self.model_name != "tiny":
                self.logger.info("Attempting fallback to 'tiny' model...")
                try:
                    self.model = WhisperModel("tiny", device=self.device, download_root=cache_dir)
                    self._model_loaded = True
                    self.logger.info("Fallback to tiny model successful")
                except Exception as fallback_error:
                    self.logger.error(f"Fallback model also failed: {fallback_error}")
                    raise
            else:
                raise
                
    async def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio data to text"""
        try:
            # Ensure model is loaded
            self._load_model()
            
            if self.model is None:
                raise RuntimeError("Whisper model not available")
                
            # Ensure audio is in the right format for Whisper
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
                
            # Normalize audio to [-1, 1] range if needed
            max_val = np.abs(audio_data).max()
            if max_val > 1.0:
                audio_data = audio_data / max_val
                
            # Transcribe
            segments, info = self.model.transcribe(
                audio_data,
                language=self.language,
                beam_size=1,  # Faster inference
                best_of=1,    # Faster inference
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments into single text
            transcription_parts = []
            for segment in segments:
                transcription_parts.append(segment.text.strip())
                
            transcription = " ".join(transcription_parts).strip()
            
            if transcription:
                self.logger.info(f"Transcription completed (language: {info.language})")
                self.logger.debug(f"Raw transcription: {transcription}")
            else:
                self.logger.warning("No speech detected in audio")
                
            return transcription
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return ""
            
    def get_available_models(self):
        """Get list of available Whisper models"""
        return ["tiny", "base", "small", "medium", "large-v2", "large-v3", "turbo"]
        
    def get_model_info(self):
        """Get information about the loaded model"""
        if not self._model_loaded or self.model is None:
            return None
            
        return {
            "model_name": self.model_name,
            "device": self.device,
            "language": self.language
        }