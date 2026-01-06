import sounddevice as sd
import numpy as np

def callback(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    print(f"Mic level: {volume_norm:.2f}")

print("🎙️ Speak into the mic. Press Ctrl+C to stop.")
with sd.InputStream(callback=callback):
    while True:
        pass