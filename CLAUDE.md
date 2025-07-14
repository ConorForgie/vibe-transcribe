# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vibe Transcribe is a cross-platform voice transcription app with global hotkeys, local Whisper transcription, and LLM-powered text improvement. The app runs as a background CLI process that captures audio via global hotkeys, transcribes using local Whisper models, processes text through LLM APIs, and outputs results to the clipboard.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application (background process)
python main.py

# Configure settings interactively
python main.py --config

# Test components
python main.py --test-audio
python main.py --test-whisper
python main.py --show-config
```

## Architecture Overview

This is a Python CLI application with a modular architecture:

- **Entry Point**: `main.py` - CLI interface using Typer
- **Configuration**: `config.py` - All settings including hotkeys, Whisper models, LLM providers, and processing mode prompts
- **Audio Module**: `audio/` - Global hotkey handling and audio recording to memory
- **Transcription Module**: `transcription/` - Local Whisper integration for speech-to-text
- **Processing Module**: `processing/` - LLM client for text improvement with 8 processing modes
- **Utilities**: `utils/` - Clipboard operations and optional logging

## Key Technical Details

### Memory-Only Design
- Audio is captured and processed entirely in memory - no disk writes
- Raw audio buffers are passed directly to Whisper models
- Results go directly to system clipboard

### Processing Flow
1. Global hotkey triggers audio recording
2. Audio buffer sent to local Whisper for transcription
3. Raw transcription processed through selected LLM mode
4. Improved text copied to clipboard
5. Graceful fallback to raw transcription if LLM fails

### LLM Integration
- Supports OpenAI API and remote Ollama (OpenAI-compatible)
- 8 processing modes: transcribe, summarize, prompt, meeting, email, code, tasks, qa
- Mode-specific prompts defined in `config.py:PROCESSING_MODES`
- Fallback handling for API failures

### Configuration System
All settings in `config.py`:
- `HOTKEYS`: Global hotkey bindings (toggle/hold modes)
- `WHISPER`: Model selection and language settings
- `LLM_PROVIDERS`: API keys and endpoints for OpenAI/Ollama
- `PROCESSING_MODES`: System prompts for each text processing mode
- `AUDIO`: Sample rate and format settings optimized for Whisper

## Development Notes

- This is currently a specification/planning project - implementation files in `audio/`, `transcription/`, `processing/`, and `utils/` directories don't exist yet
- The actual codebase only contains configuration and documentation files
- When implementing, follow the modular structure outlined in SPEC.md and README.md
- Cross-platform compatibility required (Windows, Linux, WSL)
- Error handling should be graceful - app should not crash on component failures

## Logging Standards

- Set up logging only in the main entry point (main.py) using `logging.basicConfig()`
- Use `setup_logging()` function from `utils.logger` at the start of each command
- In modules, use `logger = logging.getLogger(__name__)` to get module-specific loggers
- Do not pass logger instances between modules - each module gets its own logger