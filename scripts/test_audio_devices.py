#!/usr/bin/env python3
import sounddevice as sd

print("Available audio devices:")
try:
    devices = sd.query_devices()
    print(devices)
except Exception as e:
    print(f"Error querying devices: {e}")

print("\nDefault input device:")
try:
    default_input = sd.default.device[0]
    print(f"Default input device ID: {default_input}")
except Exception as e:
    print(f"Error getting default input: {e}")