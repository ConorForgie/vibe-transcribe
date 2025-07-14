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

On Linux systems, you'll need to install kernel headers for the global hotkey functionality:

```bash
sudo apt-get install build-essential linux-headers-generic
```

**For WSL users:** You'll also need X11 forwarding for hotkey support. Either:
- Use WSL2 with WSLg (Windows 11) - should work out of the box
- Or set up X11 forwarding with VcXsrv/Xming and `export DISPLAY=:0`

### Installation

```bash
# Install dependencies with pixi
pixi install

# Or with pip
pip install -r requirements.txt

# Run with default settings
pixi run start
# Or: python main.py

# Configure hotkeys and models
pixi run config
# Or: python main.py --config
```

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