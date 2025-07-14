#!/usr/bin/env python3
"""
Vibe Transcribe - Voice transcription with global hotkeys and LLM processing
"""
import asyncio
import logging
from typing import Optional
import typer
from pathlib import Path
import os
import signal
import sys

import config
from audio.recorder import AudioRecorder
from transcription.whisper_client import WhisperClient
from processing.llm_client import LLMClient
from utils.clipboard import ClipboardManager
from utils.logger import setup_logging

app = typer.Typer(help="Vibe Transcribe - Voice transcription with global hotkeys")

# State file for tracking recording status
STATE_FILE = Path("/tmp/vibe-transcribe.state")

class VibeTranscribe:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clipboard = ClipboardManager()
        self.whisper = WhisperClient(config.WHISPER)
        self.llm = LLMClient(config.LLM_PROVIDERS, config.DEFAULT_PROVIDER)
        self.recorder = AudioRecorder(config.AUDIO)
        self.recording_process = None
        
    def is_recording(self) -> bool:
        """Check if currently recording based on state file"""
        return STATE_FILE.exists()
        
    def set_recording_state(self, recording: bool, pid: int = None):
        """Set recording state"""
        if recording:
            STATE_FILE.write_text(str(pid or os.getpid()))
        else:
            STATE_FILE.unlink(missing_ok=True)
            
    def get_recording_pid(self) -> Optional[int]:
        """Get PID of recording process"""
        if STATE_FILE.exists():
            try:
                return int(STATE_FILE.read_text().strip())
            except (ValueError, FileNotFoundError):
                return None
        return None
        
    def kill_recording_process(self):
        """Kill existing recording process"""
        pid = self.get_recording_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                self.logger.info(f"Stopped recording process {pid}")
            except ProcessLookupError:
                self.logger.warning(f"Recording process {pid} not found")
            except PermissionError:
                self.logger.error(f"Permission denied to kill process {pid}")
        self.set_recording_state(False)
        
    def _start_recording(self):
        """Start audio recording"""
        try:
            self.recorder.start_recording()
            self.logger.info("🎤 Recording started...")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            
    async def _stop_and_process(self, mode: str):
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
            if mode != "transcribe":
                self.logger.info(f"🧠 Processing with mode: {mode}")
                try:
                    processed_text = await self.llm.process_text(transcription, mode)
                    final_text = processed_text
                except Exception as e:
                    self.logger.warning(f"LLM processing failed, using transcription: {e}")
                    final_text = transcription
            else:
                final_text = transcription
                
            # Copy to clipboard
            if self.clipboard.copy_to_clipboard(final_text):
                self.logger.info("✅ Text copied to clipboard")
            else:
                self.logger.info("📝 Clipboard failed, printing result:")
                print(final_text)
                
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
        finally:
            self.set_recording_state(False)
            
    async def record_toggle(self, mode: str = None):
        """Toggle recording on/off"""
        if self.is_recording():
            # Stop existing recording
            self.kill_recording_process()
            return
            
        # Start new recording
        mode = mode or config.DEFAULT_MODE
        self.logger.info(f"🎤 Starting recording in {mode} mode...")
        self.set_recording_state(True)
        
        try:
            self.recorder.start_recording()
            self.logger.info("🎤 Recording... Press Ctrl+Alt+T again to stop")
            
            # Keep recording until interrupted
            while self.is_recording():
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Recording stopped by user")
        finally:
            await self._stop_and_process(mode)
            
    async def record_hold(self, mode: str = None):
        """Record while process is running"""
        mode = mode or config.DEFAULT_MODE
        self.logger.info(f"🎤 Hold recording in {mode} mode...")
        self.set_recording_state(True)
        
        try:
            self.recorder.start_recording()
            self.logger.info("🎤 Recording... Release hotkey to stop")
            
            # Keep recording until interrupted
            while True:
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Recording stopped")
        finally:
            await self._stop_and_process(mode)
            self.set_recording_state(False)

@app.command()
def record(
    mode: str = typer.Option(None, "--mode", "-m", help="Processing mode"),
    hold: bool = typer.Option(False, "--hold", help="Hold to record mode")
):
    """Start recording (toggle or hold mode)"""
    setup_logging(config.LOG_FILE)
    vibe = VibeTranscribe()
    
    # Use default mode if not specified
    mode = mode or config.DEFAULT_MODE
    
    # Validate mode
    if mode not in config.PROCESSING_MODES:
        typer.echo(f"❌ Invalid mode: {mode}")
        typer.echo(f"Available modes: {list(config.PROCESSING_MODES.keys())}")
        raise typer.Exit(1)
    
    if hold:
        asyncio.run(vibe.record_hold(mode))
    else:
        asyncio.run(vibe.record_toggle(mode))

@app.command()
def stop():
    """Stop any active recording"""
    setup_logging(config.LOG_FILE)
    vibe = VibeTranscribe()
    
    if vibe.is_recording():
        vibe.kill_recording_process()
        typer.echo("🛑 Recording stopped")
    else:
        typer.echo("ℹ️  No active recording")

@app.command()
def status():
    """Show recording status"""
    vibe = VibeTranscribe()
    
    if vibe.is_recording():
        pid = vibe.get_recording_pid()
        typer.echo(f"🎤 Recording active (PID: {pid})")
    else:
        typer.echo("🟢 Ready to record")

@app.command()
def config_setup():
    """Interactive configuration setup"""
    typer.echo("🔧 Configuration setup coming soon...")
    typer.echo("\n💡 For now, edit config.py directly")
    typer.echo("\n🎮 External Hotkey Setup:")
    typer.echo("  Windows: Use PowerToys to map:")
    typer.echo("    Ctrl+Alt+T → pixi run python main.py record")
    typer.echo("    Ctrl+Alt+H → pixi run python main.py record --hold")
    typer.echo("  Linux: Use xbindkeys or similar")
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
    typer.echo(f"  Whisper Model: {config.WHISPER['model']}")
    typer.echo(f"  Default Provider: {config.DEFAULT_PROVIDER}")
    typer.echo(f"  Default Mode: {config.DEFAULT_MODE}")
    typer.echo(f"  Available Modes: {list(config.PROCESSING_MODES.keys())}")
    typer.echo("\n🎯 CLI Usage:")
    typer.echo("  Toggle recording: python main.py record")
    typer.echo("  Hold recording: python main.py record --hold")
    typer.echo("  Stop recording: python main.py stop")
    typer.echo("  Check status: python main.py status")

if __name__ == "__main__":
    app()