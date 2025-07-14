# Vibe Transcribe

A cross-platform voice transcription app with global hotkeys, local Whisper transcription, and LLM-powered text improvement.

## Features

- **CLI-Based Recording**: Toggle or hold-to-record via command line
- **External Hotkey Support**: Works with PowerToys (Windows) or xbindkeys (Linux)
- **Local Transcription**: Uses OpenAI Whisper for offline speech-to-text
- **LLM Text Improvement**: Multiple processing modes using OpenAI API or remote Ollama
- **Memory-Only**: No disk writes - results go directly to clipboard
- **Cross-Platform**: Works on Windows, Linux, and WSL
- **State Management**: Tracks recording status across processes

## Processing Modes

1. **transcribe** - Clean transcription (remove ums, ahs, fix grammar)
2. **summarize** - Condense content while keeping key points
3. **prompt** - Format as well-structured LLM prompt
4. **meeting** - Structure as meeting notes with action items
5. **email** - Format as professional email
6. **code** - Format as code documentation/comments
7. **tasks** - Extract actionable items/todos
8. **qa** - Structure as questions and answers

## Quick Start

### Prerequisites

On Linux/WSL systems, you'll need to install system dependencies:

```bash
# Required system packages
sudo apt install build-essential linux-headers-generic portaudio19-dev pulseaudio pulseaudio-utils

# For WSL2 users, also needed for audio support
sudo apt install alsa-utils
```

### Installation

```bash
# Install dependencies with pixi (recommended)
pixi install

# Basic usage (CLI commands)
pixi run record           # Toggle recording on/off
pixi run record-hold      # Hold-to-record mode
pixi run stop             # Stop any active recording
pixi run status           # Check recording status

# Test components
pixi run test-audio
pixi run test-whisper
pixi run show-config

# Configure settings
pixi run config
```

### WSL2 Setup (Windows Users)

For WSL2 users, additional setup is required for audio and X11 support:

#### 1. X11 Display Setup
```bash
# Add to ~/.bashrc
export DISPLAY=:0
```

#### 2. PulseAudio Setup
WSL2 uses WSLg which provides PulseAudio support:

```bash
# Add to ~/.bashrc
export PULSE_SERVER=unix:/mnt/wslg/PulseServer

# Test PulseAudio connection
pactl info

# Should show:
# Server String: unix:/mnt/wslg/PulseServer
# Default Source: RDPSource
```

#### 3. Verify Audio Devices
```bash
# Test audio setup
pixi run python scripts/test_soundcard.py

# Should detect:
# - Microphone: RDP Source (1 channels)
# - Speaker: RDP Sink (2 channels)
```

#### 4. Troubleshooting WSL2
If audio doesn't work:
- Ensure Windows microphone permissions are enabled
- Check WSLg version: `wsl --version` (need WSLg 1.0+)
- Restart WSL: `wsl --shutdown` then `wsl` in Windows PowerShell

## Global Hotkey Setup

Since this app uses a CLI-based approach, you'll need external hotkey management:

### Windows (PowerToys)

1. Install [PowerToys](https://github.com/microsoft/PowerToys)
2. Open PowerToys Settings → Keyboard Manager → Remap shortcuts
3. Add these mappings:

```
Ctrl+Alt+T → Run Command → cd /path/to/vibe-transcribe && pixi run record
Ctrl+Alt+H → Run Command → cd /path/to/vibe-transcribe && pixi run record-hold
```

### Linux/WSL

Create `~/.xbindkeysrc`:

```bash
# Toggle recording
"cd /path/to/vibe-transcribe && pixi run record"
    control+alt + t

# Hold recording  
"cd /path/to/vibe-transcribe && pixi run record-hold"
    control+alt + h
```

Then run: `xbindkeys`

### macOS

Use Karabiner-Elements or similar to map hotkeys to shell commands.

## Architecture

```
main.py (CLI entry point with state management)
├── audio/
│   └── recorder.py (audio capture via soundcard)
├── transcription/
│   └── whisper_client.py (local Whisper integration)
├── processing/
│   ├── llm_client.py (OpenAI/Ollama API client)
│   └── modes.py (text processing modes)
├── utils/
│   ├── clipboard.py (clipboard operations)
│   └── logger.py (logging setup)
└── config.py (configuration settings)
```

## CLI Commands

```bash
# Recording commands
pixi run record                    # Toggle recording on/off
pixi run record --mode summarize   # Toggle with specific mode
pixi run record --hold             # Hold-to-record mode
pixi run stop                      # Stop active recording
pixi run status                    # Check recording status

# Testing commands
pixi run test-audio                # Test audio capture
pixi run test-whisper              # Test Whisper transcription
pixi run show-config               # Show current configuration
```