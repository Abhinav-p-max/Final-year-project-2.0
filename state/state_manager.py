import threading


class StateManager:
    """
    Thread-safe state manager for system modes.
    States: IDLE, MOUSE_ACTIVE, KEYBOARD_ACTIVE
    """

    IDLE = "IDLE"
    MOUSE = "MOUSE_ACTIVE"
    KEYBOARD = "KEYBOARD_ACTIVE"

    def __init__(self):
        self._state = self.IDLE
        self._lock = threading.Lock()

    def set_state(self, new_state: str):
        with self._lock:
            if new_state != self._state:
                print(f"[STATE] {self._state} -> {new_state}")
                self._state = new_state

    def get_state(self) -> str:
        with self._lock:
            return self._state