# Vibe Transcribe - Technical Specification

## Core Requirements

### 1. Audio Recording
- **Global Hotkeys**: 
  - Toggle mode: Press once to start, press again to stop
  - Hold mode: Hold key to record, release to stop
- **Audio Format**: WAV in memory, no disk writes
- **Cross-platform**: Must work on Windows and WSL/Linux

### 2. Speech-to-Text
- **Local Whisper**: Use OpenAI Whisper models locally
- **Model Selection**: Configurable (tiny, base, small, medium, large, turbo)
- **Language**: Auto-detect or configurable
- **In-Memory**: No audio files written to disk

### 3. Text Processing
- **LLM Providers**: 
  - OpenAI API (GPT-4, GPT-3.5-turbo)
  - Remote Ollama (treated as OpenAI-compatible API)
- **Processing Modes**: 8 different text improvement modes
- **Fallback**: If LLM fails, return clean transcription

### 4. Output
- **Primary**: Copy result to system clipboard
- **Optional**: Log to text file with timestamps
- **Format**: Plain text, ready to paste anywhere

## Technical Implementation

### Dependencies
```
typer          # CLI interface
openai-whisper # Local speech-to-text
pynput         # Global hotkeys
sounddevice    # Audio recording
soundfile      # Audio file handling
pyperclip      # Clipboard operations
requests       # HTTP client for APIs
```

### Configuration System
Simple Python config file (`config.py`) with:
- Hotkey bindings
- Whisper model selection
- LLM provider settings (API keys, endpoints)
- Default processing mode
- Log file path (optional)

### Audio Recording Flow
1. Register global hotkeys on startup
2. On hotkey trigger:
   - Start audio recording to memory buffer
   - Show recording indicator (CLI output)
   - Stop on second hotkey press or key release
3. Pass audio buffer to transcription

### Transcription Flow
1. Load Whisper model (cached after first use)
2. Transcribe audio buffer directly from memory
3. Return raw transcription text
4. Handle errors gracefully

### Text Processing Flow
1. Take raw transcription
2. Apply selected processing mode
3. Send to configured LLM provider
4. Return improved text
5. Fallback to raw transcription on errors

### Error Handling
- Audio recording failures: Show error, don't crash
- Whisper model loading: Retry with smaller model
- LLM API failures: Return transcription without processing
- Clipboard failures: Print to console as backup

## CLI Interface

### Commands
```bash
# Start the app (runs in background)
python main.py

# Configure settings
python main.py --config

# Test recording
python main.py --test-audio

# Test transcription
python main.py --test-whisper

# Show current config
python main.py --show-config
```

### Runtime Usage
- App runs in background
- Global hotkeys work from any application
- Status updates printed to console
- Ctrl+C to exit

## File Structure
```
vibe-transcribe/
├── main.py                 # CLI entry point
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── audio/
│   ├── __init__.py
│   ├── recorder.py        # Audio capture logic
│   └── hotkeys.py         # Global hotkey handling
├── transcription/
│   ├── __init__.py
│   └── whisper_client.py  # Whisper integration
├── processing/
│   ├── __init__.py
│   ├── llm_client.py      # LLM API client
│   └── modes.py           # Text processing modes
└── utils/
    ├── __init__.py
    ├── clipboard.py       # Clipboard operations
    └── logger.py          # Optional logging
```

## Processing Mode Prompts

Each mode will have a specific system prompt for the LLM:

1. **transcribe**: "Clean up this transcription by removing filler words, fixing grammar, and improving punctuation while preserving the original meaning and tone."

2. **summarize**: "Summarize this transcription concisely while preserving all key points and important details."

3. **prompt**: "Format this transcription as a clear, well-structured prompt for an AI assistant."

4. **meeting**: "Format this transcription as professional meeting notes with clear action items, decisions, and key discussion points."

5. **email**: "Format this transcription as a professional email with appropriate greeting, body, and closing."

6. **code**: "Format this transcription as clear code documentation or comments."

7. **tasks**: "Extract all actionable items, tasks, and todos from this transcription and format as a numbered list."

8. **qa**: "Structure this transcription as a clear question and answer format."

## Configuration Example

```python
# config.py
HOTKEYS = {
    "toggle": "ctrl+alt+t",
    "hold": "ctrl+alt+h"
}

WHISPER = {
    "model": "base",  # tiny, base, small, medium, large, turbo
    "language": None  # Auto-detect
}

LLM_PROVIDERS = {
    "openai": {
        "api_key": "your-api-key",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4"
    },
    "ollama": {
        "api_key": "",  # Not needed for Ollama
        "base_url": "http://your-ollama-server:11434/v1",
        "model": "llama3"
    }
}

DEFAULT_PROVIDER = "openai"
DEFAULT_MODE = "transcribe"
LOG_FILE = None  # Set to path for logging
```