#!/usr/bin/env python3
import soundcard as sc
import numpy as np

print("=== SoundCard Library Test ===")

try:
    # Get default microphone
    print("1. Getting default microphone...")
    default_mic = sc.default_microphone()
    print(f"Default microphone: {default_mic}")
    
    # List all microphones
    print("\n2. Available microphones:")
    mics = sc.all_microphones()
    for i, mic in enumerate(mics):
        print(f"  {i}: {mic}")
    
    # List all speakers
    print("\n3. Available speakers:")
    speakers = sc.all_speakers()
    for i, speaker in enumerate(speakers):
        print(f"  {i}: {speaker}")
    
    # Try to record for 2 seconds
    print("\n4. Testing recording (2 seconds)...")
    if default_mic:
        sample_rate = 16000
        duration = 2
        
        print(f"Recording {duration}s at {sample_rate}Hz...")
        data = default_mic.record(samplerate=sample_rate, numframes=sample_rate * duration)
        
        print(f"Success! Recorded {len(data)} samples")
        print(f"Audio level: min={np.min(data):.4f}, max={np.max(data):.4f}, rms={np.sqrt(np.mean(data**2)):.4f}")
    else:
        print("No default microphone available")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()