import time
import os
import threading

from state.state_manager import StateManager
from voice.voice_listener import VoiceListener
from vision.mouse_controller import MouseController
from vision.keyboard_controller import KeyboardGestureController
from ui.virtual_keyboard import VirtualKeyboard


def main():
    state_manager = StateManager()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    vosk_model_path = os.path.join(base_dir, "vosk-model-small-en-us-0.15")

    voice_listener = VoiceListener(state_manager, vosk_model_path)
    voice_listener.start()

    mouse_controller = MouseController(state_manager)
    keyboard = VirtualKeyboard(state_manager)
    keyboard_controller = KeyboardGestureController(state_manager, keyboard)

    kb_thread = None

    print("✅ System running.")
    print("Say: 'open mouse' or 'open keyboard'")
    print("Press Ctrl+C to exit.")

    try:
        while True:
            state = state_manager.get_state()

            if state == StateManager.MOUSE:
                print("🖱️ Mouse mode activated")
                mouse_controller.run()
                print("🖱️ Mouse mode stopped")

            elif state == StateManager.KEYBOARD:
                print("⌨️ Keyboard mode activated")

                kb_thread = threading.Thread(
                    target=keyboard_controller.run, daemon=True
                )
                kb_thread.start()

                keyboard.show()

                print("⌨️ Keyboard mode stopped")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n🛑 Exiting system...")
        voice_listener.stop()


if __name__ == "__main__":
    main()
