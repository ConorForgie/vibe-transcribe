# Vibe Transcribe

A cross-platform voice transcription app with global hotkeys, local Whisper transcription, and LLM-powered text improvement.

## Features

- **Global Hotkeys**: Toggle or hold-to-record voice input from anywhere
- **Local Transcription**: Uses OpenAI Whisper for offline speech-to-text
- **LLM Text Improvement**: Multiple processing modes using OpenAI API or remote Ollama
- **Memory-Only**: No disk writes - results go directly to clipboard
- **Cross-Platform**: Works on Windows, Linux, and WSL
- **CLI Interface**: Lightweight background process

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

# Run with default settings
pixi run start

# Test components
pixi run test-audio
pixi run test-whisper
pixi run show-config

# Configure hotkeys and models
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

## Architecture

```
main.py (CLI entry point)
├── audio/
│   ├── recorder.py (audio capture)
│   └── hotkeys.py (global hotkey handling)
├── transcription/
│   └── whisper_client.py (local Whisper integration)
├── processing/
│   ├── llm_client.py (OpenAI/Ollama API client)
│   └── modes.py (text processing modes)
├── utils/
│   ├── clipboard.py (clipboard operations)
│   └── logger.py (optional logging)
└── config.py (configuration settings)
```