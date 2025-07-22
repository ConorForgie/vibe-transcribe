#!/usr/bin/env python3
"""
Vibe Transcribe - Voice transcription with global hotkeys and LLM processing
"""
import os
# Fix OpenMP library conflict on Windows
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import asyncio
import logging
from typing import Optional
import typer
from pathlib import Path

import config
from audio.hotkeys import HotkeyManager
from audio.recorder import AudioRecorder
from transcription.whisper_client import WhisperClient
from processing.llm_client import LLMClient
from utils.clipboard import ClipboardManager
from utils.logger import setup_logging

app = typer.Typer(help="Vibe Transcribe - Voice transcription with global hotkeys")

class VibeTranscribe:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clipboard = ClipboardManager()
        self.whisper = WhisperClient(config.WHISPER)
        self.llm = LLMClient(config.LLM_PROVIDERS, config.DEFAULT_PROVIDER)
        self.recorder = AudioRecorder(config.AUDIO)
        self.hotkey_manager = HotkeyManager(config.HOTKEYS)
        
        # Set up callbacks
        self.hotkey_manager.set_callbacks(
            toggle_callback=self._handle_toggle_recording,
            hold_start_callback=self._handle_start_recording,
            hold_end_callback=self._handle_stop_recording
        )
        
    async def _handle_toggle_recording(self):
        """Handle toggle recording hotkey"""
        if self.recorder.is_recording:
            await self._stop_and_process()
        else:
            self._start_recording()
            
    async def _handle_start_recording(self):
        """Handle start of hold-to-record"""
        self._start_recording()
        
    async def _handle_stop_recording(self):
        """Handle end of hold-to-record"""
        await self._stop_and_process()
        
    def _start_recording(self):
        """Start audio recording"""
        try:
            self.recorder.start_recording()
            self.logger.info("🎤 Recording started...")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            
    async def _stop_and_process(self):
        """Stop recording and process audio"""
        try:
            audio_data = self.recorder.stop_recording()
            if audio_data is None:
                self.logger.warning("No audio data captured")
                return

            self.logger.info("🔄 Transcribing...")
            transcription = await self.whisper.transcribe(audio_data)

            if not transcription.strip():
                self.logger.warning("No speech detected")
                return

            # Process with LLM if not just transcribe mode
            if config.DEFAULT_MODE != "transcribe":
                self.logger.info(f"🧠 Processing with mode: {config.DEFAULT_MODE}")
                try:
                    processed_text = await self.llm.process_text(transcription, config.DEFAULT_MODE)
                    final_text = processed_text
                except Exception as e:
                    self.logger.warning(f"LLM processing failed, using transcription: {e}")
                    final_text = transcription
            else:
                final_text = transcription

            self.logger.info(f"Transcribed text[:50] = {final_text[:50]}")
            # Copy to clipboard
            if self.clipboard.copy_to_clipboard(final_text):
                self.logger.info("✅ Text copied to clipboard")
            else:
                self.logger.info("📝 Clipboard failed")

        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            
    async def run(self):
        """Main application loop"""
        self.logger.info("🚀 Vibe Transcribe starting...")
        self.logger.info(f"🎯 Mode: {config.DEFAULT_MODE}")
        self.logger.info(f"🔥 Hotkeys: {config.HOTKEYS}")
        
        try:
            # Start hotkey listeners
            self.hotkey_manager.start()
            self.logger.info("🎮 Hotkeys active - Press Ctrl+C to exit")
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("👋 Shutting down...")
        finally:
            self.hotkey_manager.stop()

@app.command()
def start():
    """Start the transcription service"""
    setup_logging(config.LOG_FILE)
    vibe = VibeTranscribe()
    asyncio.run(vibe.run())

@app.command()
def config_setup():
    """Interactive configuration setup"""
    typer.echo("🔧 Configuration setup coming soon...")
    # TODO: Implement interactive config

@app.command()
def test_audio():
    """Test audio recording"""
    setup_logging()
    logger = logging.getLogger(__name__)
    recorder = AudioRecorder(config.AUDIO)
    
    logger.info("🎤 Testing audio recording for 3 seconds...")
    recorder.start_recording()
    import time
    time.sleep(3)
    audio_data = recorder.stop_recording()
    
    if audio_data is not None:
        logger.info(f"✅ Audio captured: {len(audio_data)} samples")
    else:
        logger.info("❌ No audio captured")

@app.command()
def test_whisper():
    """Test Whisper transcription"""
    setup_logging()
    logger = logging.getLogger(__name__)
    whisper = WhisperClient(config.WHISPER)
    
    logger.info("🎤 Testing Whisper - speak for 3 seconds...")
    recorder = AudioRecorder(config.AUDIO)
    recorder.start_recording()
    import time
    time.sleep(3)
    audio_data = recorder.stop_recording()
    
    if audio_data is not None:
        logger.info("🔄 Transcribing...")
        result = asyncio.run(whisper.transcribe(audio_data))
        logger.info(f"📝 Result: {result}")
    else:
        logger.info("❌ No audio to transcribe")

@app.command() 
def show_config():
    """Display current configuration"""
    typer.echo("📋 Current Configuration:")
    typer.echo(f"  Hotkeys: {config.HOTKEYS}")
    typer.echo(f"  Whisper Model: {config.WHISPER['model']}")
    typer.echo(f"  Default Provider: {config.DEFAULT_PROVIDER}")
    typer.echo(f"  Default Mode: {config.DEFAULT_MODE}")
    typer.echo(f"  Available Modes: {list(config.PROCESSING_MODES.keys())}")

if __name__ == "__main__":
    app()