import tkinter as tk
from functools import partial
import pyautogui

from state.state_manager import StateManager

# Simple list of common words for prediction
COMMON_WORDS = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "i", 
                "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", 
                "this", "but", "his", "by", "from", "they", "we", "say", "her", 
                "she", "or", "an", "will", "my", "one", "all", "would", "there", 
                "their", "what", "so", "up", "out", "if", "about", "who", "get", 
                "which", "go", "me", "when", "make", "can", "like", "time", "no", 
                "just", "him", "know", "take", "people", "into", "year", "your", 
                "good", "some", "could", "them", "see", "other", "than", "then", 
                "now", "look", "only", "come", "its", "over", "think", "also", 
                "back", "after", "use", "two", "how", "our", "work", "first", 
                "well", "way", "even", "new", "want", "because", "any", "these", 
                "give", "day", "most", "us"]


class VirtualKeyboard:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.root = None
        self.visible = False

        self.keys = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"],
            ["SPACE", "BSPACE", "ENTER"],
        ]
        
        # Suggestions state
        self.current_word = ""
        self.suggestion_buttons = []
        self.suggestions = ["", "", ""]

        self.buttons = {}
        self.default_bg = None

    def press_key(self, key: str):
        if key == "SPACE":
            pyautogui.press("space")
            self.current_word = "" # Reset word
            self.update_suggestions()
        elif key == "BSPACE":
            pyautogui.press("backspace")
            self.current_word = self.current_word[:-1]
            self.update_suggestions()
        elif key == "ENTER":
            pyautogui.press("enter")
            self.current_word = ""
            self.update_suggestions()
        else:
            pyautogui.press(key.lower())
            self.current_word += key.lower()
            self.update_suggestions()
            
    def select_suggestion(self, index):
        if 0 <= index < len(self.suggestions):
            word = self.suggestions[index]
            if word:
                # Delete what we typed so far
                for _ in range(len(self.current_word)):
                    pyautogui.press("backspace")
                
                # Type the full word + space
                pyautogui.write(word)
                pyautogui.press("space")
                
                self.current_word = ""
                self.update_suggestions()

    def update_suggestions(self):
        if not self.root:
            return
            
        if not self.current_word:
            self.suggestions = ["", "", ""]
        else:
            matches = [w for w in COMMON_WORDS if w.startswith(self.current_word.lower())]
            # Pick top 3
            self.suggestions = (matches[:3] + ["", "", ""])[:3]
            
        # Update UI
        for i, btn in enumerate(self.suggestion_buttons):
            btn.config(text=self.suggestions[i])

    def _on_key_press(self, key):
        self.press_key(key)
        
    def _on_suggestion_click(self, index):
        self.select_suggestion(index)

    # -------- Thread-safe UI updates --------
    def highlight_key(self, key):
        if self.root:
            self.root.after(0, self._highlight_key_ui, key)

    def _highlight_key_ui(self, key):
        for btn in self.buttons.values():
            btn.config(bg=self.default_bg)
        if key in self.buttons:
            self.buttons[key].config(bg="yellow")
            
    # Highlight suggestions if requested (mapped to specific coordinates or gesture)
    def highlight_suggestion(self, index):
        if self.root:
            self.root.after(0, self._highlight_suggestion_ui, index)
            
    def _highlight_suggestion_ui(self, index):
        # Clear previous highlights
        for btn in self.suggestion_buttons:
             btn.config(bg=self.default_bg if self.default_bg else "SystemButtonFace")
             
        if 0 <= index < len(self.suggestion_buttons):
            self.suggestion_buttons[index].config(bg="cyan")

    def clear_highlight(self):
        if self.root:
            self.root.after(0, self._clear_highlight_ui)

    def _clear_highlight_ui(self):
        for btn in self.buttons.values():
            btn.config(bg=self.default_bg)
        for btn in self.suggestion_buttons:
             btn.config(bg=self.default_bg if self.default_bg else "SystemButtonFace")

    # ---------------------------------------

    def _poll_state(self):
        if self.state_manager.get_state() != StateManager.KEYBOARD:
            self.hide()
        elif self.root:
            self.root.after(200, self._poll_state)

    def show(self):
        if self.visible:
            return

        self.root = tk.Tk()
        self.root.title("Virtual Keyboard")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        # --- Suggestion Row ---
        suggestion_frame = tk.Frame(self.root)
        suggestion_frame.grid(row=0, column=0, columnspan=10, padx=5, pady=5)
        
        self.suggestion_buttons = []
        for i in range(3):
            btn = tk.Button(suggestion_frame, text="", width=20, height=2, font=("Arial", 12, "bold"),
                           command=partial(self._on_suggestion_click, i))
            btn.pack(side=tk.LEFT, padx=5)
            self.suggestion_buttons.append(btn)
            
        # --- Keys ---
        key_frame = tk.Frame(self.root)
        key_frame.grid(row=1, column=0, padx=5, pady=5)

        for r, row in enumerate(self.keys):
            for c, key in enumerate(row):
                btn = tk.Button(
                    key_frame,
                    text=key,
                    width=8,
                    height=3,
                    font=("Arial", 12),
                    command=partial(self._on_key_press, key),
                )
                btn.grid(row=r, column=c, padx=3, pady=3)

                if self.default_bg is None:
                    self.default_bg = btn.cget("bg")
                self.buttons[key] = btn

        # Dock to right
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = self.root.winfo_reqwidth()
        wh = self.root.winfo_reqheight()

        x = sw - ww - 20
        y = (sh - wh) // 2
        self.root.geometry(f"+{x}+{y}")

        self.visible = True
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.update_suggestions()

        self.root.after(200, self._poll_state)
        self.root.mainloop()

    def hide(self):
        if self.root:
            self.visible = False
            self.root.destroy()
            self.root = None
