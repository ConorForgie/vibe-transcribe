# Vibe Transcribe Configuration

# Global Hotkeys
HOTKEYS = {
    "toggle": "ctrl+alt+t",  # Press once to start, press again to stop
    "hold": "ctrl+alt+h"     # Hold to record, release to stop
}

# Whisper Configuration
WHISPER = {
    "model": "base",    # Options: tiny, base, small, medium, large, turbo
    "language": None,   # Auto-detect language (or specify like "en", "es", etc.)
    "device": "cpu"     # Options: "cpu", "cuda" (if available)
}

# LLM Provider Configuration
LLM_PROVIDERS = {
    "openai": {
        "api_key": "",  # Set your OpenAI API key
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4"
    },
    "ollama": {
        "api_key": "",  # Not needed for Ollama
        "base_url": "http://localhost:11434/v1",  # Change to your Ollama server
        "model": "llama3"
    }
}

# Default Settings
DEFAULT_PROVIDER = "openai"
DEFAULT_MODE = "transcribe"

# Audio Settings
AUDIO = {
    "sample_rate": 16000,  # Whisper works best with 16kHz
    "channels": 1,         # Mono audio
    "dtype": "float32",
    "max_duration": 300    # Maximum recording duration in seconds (5 minutes)
}

# Optional Logging
LOG_FILE = None  # Set to a file path like "/tmp/vibe-transcribe.log" to enable logging

# Processing Modes and their prompts
PROCESSING_MODES = {
    "transcribe": "Clean up this transcription by removing filler words (um, uh, like), fixing grammar, and improving punctuation while preserving the original meaning and tone. Return only the cleaned text.",
    
    "summarize": "Summarize this transcription concisely while preserving all key points and important details. Make it clear and actionable.",
    
    "prompt": "Format this transcription as a clear, well-structured prompt for an AI assistant. Make it specific and actionable.",
    
    "meeting": "Format this transcription as professional meeting notes with clear action items, decisions, and key discussion points. Use bullet points and clear structure.",
    
    "email": "Format this transcription as a professional email with appropriate greeting, body, and closing. Make it polite and clear.",
    
    "code": "Format this transcription as clear code documentation or comments. Make it concise and technically accurate.",
    
    "tasks": "Extract all actionable items, tasks, and todos from this transcription and format as a numbered list. Be specific about what needs to be done.",
    
    "qa": "Structure this transcription as a clear question and answer format. Separate questions and answers clearly."
}