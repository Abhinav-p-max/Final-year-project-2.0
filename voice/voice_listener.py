import json
import threading
import time
import queue
import pyautogui

import sounddevice as sd
from vosk import Model, KaldiRecognizer

from state.state_manager import StateManager

class VoiceListener:
    """
    Background voice command listener using Vosk.
    Wake word required: "computer"
    """

    def __init__(self, state_manager: StateManager, model_path: str):
        self.state_manager = state_manager
        self.model_path = model_path

        print("Loading Vosk model...")
        self.model = Model(self.model_path)

        self.commands = [
            "computer open mouse",
            "computer close mouse",
            "computer open keyboard",
            "computer close keyboard",
            "computer scroll up",
            "computer scroll down",
            "computer right click",
            "computer double click",
            "computer minimize window"
        ]
        grammar = json.dumps(self.commands)

        self.recognizer = KaldiRecognizer(self.model, 16000, grammar)
        self.recognizer.SetWords(True)

        self.audio_queue = queue.Queue()
        self._stop = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

        self.last_command_time = 0
        self.cooldown = 1.6 # Slightly reduced cooldown for utility commands
        self.confidence_threshold = 0.75

    def start(self):
        self.thread.start()
        print("Voice listener started.")
        print("Commands: Open/Close [Mouse/Keyboard], Scroll Up/Down, Right/Double Click, Minimize Window")

    def stop(self):
        self._stop.set()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.audio_queue.put(bytes(indata))

    def _safe_switch(self, new_state):
        current = self.state_manager.get_state()
        if current != StateManager.IDLE:
            self.state_manager.set_state(StateManager.IDLE)
            time.sleep(0.3)
        self.state_manager.set_state(new_state)

    def _average_confidence(self, result_json: dict) -> float:
        words = result_json.get("result", [])
        if not words:
            return 0.0
        return sum(w.get("conf", 0.0) for w in words) / len(words)

    def _handle_command(self, text: str):
        now = time.time()
        if now - self.last_command_time < self.cooldown:
            return

        print(f"[VOICE] Command recognized: {text}")

        # --- UI VISUALIZATION ---
        try:
            from ui.web_server import trigger_voice_activity
            trigger_voice_activity(text)
        except:
            pass
        # ------------------------

        if text == "computer open mouse":
            self._safe_switch(StateManager.MOUSE)
        elif text == "computer close mouse":
            self.state_manager.set_state(StateManager.IDLE)
        elif text == "computer open keyboard":
            self._safe_switch(StateManager.KEYBOARD)
        elif text == "computer close keyboard":
            self.state_manager.set_state(StateManager.IDLE)
            
        # --- NEW UTILITY COMMANDS ---
        elif text == "computer scroll up":
            pyautogui.scroll(400)
        elif text == "computer scroll down":
            pyautogui.scroll(-400)
        elif text == "computer right click":
            pyautogui.rightClick()
        elif text == "computer double click":
            pyautogui.doubleClick()
        elif text == "computer minimize window":
            import ctypes
            # Windows API to minimize foreground window
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            ctypes.windll.user32.ShowWindow(hwnd, 6) # 6 = SW_MINIMIZE

        self.last_command_time = now

    def _run(self):
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        ):
            while not self._stop.is_set():
                try:
                    data = self.audio_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip().lower()

                    if text:
                        avg_conf = self._average_confidence(result)
                        print(f"[VOICE] Detected: {text} (conf={avg_conf:.2f})")

                        if text in self.commands and avg_conf >= self.confidence_threshold:
                            self._handle_command(text)
                        else:
                            print("[VOICE] Low confidence or invalid command")
