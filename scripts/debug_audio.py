#!/usr/bin/env python3
import sounddevice as sd
import numpy as np

print("=== SoundDevice Debug ===")

# Check if PortAudio can see any devices
print("\n1. Raw device query:")
try:
    devices = sd.query_devices()
    print(f"Found {len(devices)} devices")
    for i, device in enumerate(devices):
        print(f"  {i}: {device}")
except Exception as e:
    print(f"Error: {e}")

print("\n2. Default devices:")
try:
    print(f"Default input: {sd.default.device[0]}")
    print(f"Default output: {sd.default.device[1]}")
except Exception as e:
    print(f"Error: {e}")

print("\n3. Check hostapis:")
try:
    hostapis = sd.query_hostapis()
    print(f"Available host APIs: {len(hostapis)}")
    for i, api in enumerate(hostapis):
        print(f"  {i}: {api}")
except Exception as e:
    print(f"Error: {e}")

print("\n4. Try to record for 1 second (if device available):")
try:
    # Try to record from default device
    duration = 1
    sample_rate = 16000
    channels = 1
    
    print(f"Recording {duration}s at {sample_rate}Hz, {channels} channel(s)...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float32')
    sd.wait()
    print(f"Success! Recorded {len(audio)} samples")
    print(f"Audio level: min={np.min(audio):.4f}, max={np.max(audio):.4f}, rms={np.sqrt(np.mean(audio**2)):.4f}")
except Exception as e:
    print(f"Recording failed: {e}")

print("\n5. Environment check:")
import os
print(f"PULSE_SERVER: {os.getenv('PULSE_SERVER', 'not set')}")
print(f"DISPLAY: {os.getenv('DISPLAY', 'not set')}")