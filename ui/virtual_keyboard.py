import sys
import threading
import pyautogui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QFrame,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QCursor

import config
from state.state_manager import StateManager

# Common words list (same as before)
COMMON_WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", 
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", 
    "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", 
    "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", 
    "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", 
    "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us", "is", "are", "was", "were", "been",
    "has", "had", "may", "should", "call", "world", "school", "still", "try", "hand", "life", "tell", "write", "pogram", "find", "use",
    "more", "day", "could", "go", "come", "did", "number", "sound", "no", "most", "people", "my", "over", "know", "water", "than", 
    "call", "first", "who", "may", "down", "side", "been", "now", "find", "any", "new", "work", "part", "take", "get", "place", 
    "made", "live", "where", "after", "back", "little", "only", "round", "man", "year", "came", "show", "every", "good", "me", 
    "give", "our", "under", "name", "very", "through", "just", "form", "sentence", "great", "think", "say", "help", "low", "line", 
    "differ", "turn", "cause", "much", "mean", "before", "move", "right", "boy", "old", "too", "same", "tell", "does", "set", "three", 
    "want", "air", "well", "also", "play", "small", "end", "put", "home", "read", "hand", "port", "large", "spell", "add", "even", 
    "land", "here", "must", "big", "high", "such", "follow", "act", "why", "ask", "men", "change", "went", "light", "kind", "off", 
    "need", "house", "picture", "try", "us", "again", "animal", "point", "mother", "world", "near", "build", "self", "earth", "father",
    "head", "stand", "own", "page", "should", "country", "found", "answer", "school", "grow", "study", "still", "learn", "plant", 
    "cover", "food", "sun", "four", "between", "state", "keep", "eye", "never", "last", "let", "thought", "city", "tree", "cross", 
    "farm", "hard", "start", "might", "story", "saw", "far", "sea", "draw", "left", "late", "run", "don't", "while", "press", "close", 
    "night", "real", "life", "few", "north", "book", "carry", "took", "science", "eat", "room", "friend", "began", "idea", "fish", 
    "mountain", "stop", "once", "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood", "main", "open", "seem", 
    "together", "next", "white", "children", "begin", "got", "walk", "example", "ease", "paper", "group", "always", "music", "those", 
    "both", "mark", "often", "letter", "until", "mile", "river", "car", "feet", "care", "second", "enough", "plain", "girl", "usual", 
    "young", "ready", "above", "ever", "red", "list", "though", "feel", "talk", "bird", "soon", "body", "dog", "family", "direct", 
    "pose", "leave", "song", "measure", "door", "product", "black", "short", "numeral", "class", "wind", "question", "happen", 
    "complete", "ship", "area", "half", "rock", "order", "fire", "south", "problem", "piece", "told", "knew", "pass", "since", "top", 
    "whole", "king", "space", "heard", "best", "hour", "better", "true", "during", "hundred", "five", "remember", "step", "early", 
    "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing", "listen", "six", "table", "travel", "less", "morning", 
    "ten", "simple", "several", "vowel", "toward", "war", "lay", "against", "pattern", "slow", "center", "love", "person", "money", 
    "serve", "appear", "road", "map", "rain", "rule", "govern", "pull", "cold", "notice", "voice", "unit", "power", "town", "fine", 
    "certain", "fly", "fall", "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure", "star", "box", "noun", "field", 
    "rest", "correct", "able", "pound", "done", "beauty", "drive", "stood", "contain", "front", "teach", "week", "final", "gave", 
    "green", "oh", "quick", "develop", "ocean", "warm", "free", "minute", "strong", "special", "mind", "behind", "clear", "tail", 
    "produce", "fact", "street", "inch", "multiply", "nothing", "course", "stay", "wheel", "full", "force", "blue", "object", "decide", 
    "surface", "deep", "moon", "island", "foot", "system", "busy", "test", "record", "boat", "common", "gold", "possible", "plane", 
    "stead", "dry", "wonder", "laugh", "thousand", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss", "brought", "heat", 
    "snow", "tire", "bring", "yes", "distant", "fill", "east", "paint", "language", "among", "grand", "ball", "yet", "wave", "drop", 
    "heart", "am", "present", "heavy", "dance", "engine", "position", "arm", "wide", "sail", "material", "size", "vary", "settle", 
    "speak", "weight", "general", "ice", "matter", "circle", "pair", "include", "divide", "syllable", "felt", "perhaps", "pick", 
    "sudden", "count", "square", "reason", "length", "represent", "art", "subject", "region", "energy", "hunt", "probable", "bed", 
    "brother", "egg", "ride", "cell", "believe", "fraction", "forest", "sit", "race", "window", "store", "summer", "train", "sleep", 
    "prove", "lone", "leg", "exercise", "wall", "catch", "mount", "wish", "sky", "board", "joy", "winter", "sat", "written", "wild", 
    "instrument", "kept", "glass", "grass", "cow", "job", "edge", "sign", "visit", "past", "soft", "fun", "bright", "gas", "weather", 
    "month", "million", "bear", "finish", "happy", "hope", "flower", "clothe", "strange", "gone", "jump", "baby", "eight", "village", 
    "meet", "root", "buy", "raise", "solve", "metal", "whether", "push", "seven", "paragraph", "third", "shall", "held", "hair", 
    "describe", "cook", "floor", "either", "result", "burn", "hill", "safe", "cat", "century", "consider", "type", "law", "bit", 
    "coast", "copy", "phrase", "silent", "tall", "sand", "soil", "roll", "temperature", "finger", "industry", "value", "fight", "lie", 
    "beat", "excite", "natural", "view", "sense", "ear", "else", "quite", "broke", "case", "middle", "kill", "son", "lake", "moment", 
    "scale", "loud", "spring", "observe", "child", "straight", "consonant", "nation", "dictionary", "milk", "speed", "method", "organ", 
    "pay", "age", "section", "dress", "cloud", "surprise", "quiet", "stone", "tiny", "climb", "cool", "design", "poor", "lot", 
    "experiment", "bottom", "key", "iron", "single", "stick", "flat", "twenty", "skin", "smile", "crease", "hole", "trade", "melody", 
    "trip", "office", "receive", "row", "mouth", "exact", "symbol", "die", "least", "trouble", "shout", "except", "wrote", "seed", 
    "tone", "join", "suggest", "clean", "break", "lady", "yard", "rise", "bad", "blow", "oil", "blood", "touch", "grew", "cent", 
    "mix", "team", "wire", "cost", "lost", "brown", "wear", "garden", "equal", "sent", "choose", "fell", "fit", "flow", "fair", 
    "bank", "collect", "save", "control", "decimal", "gentle", "woman", "captain", "practice", "separate", "difficult", "doctor", 
    "please", "protect", "noon", "whose", "locate", "ring", "character", "insect", "caught", "period", "indicate", "radio", "spoke", 
    "atom", "human", "history", "effect", "electric", "expect", "crop", "modern", "element", "hit", "student", "corner", "party", 
    "supply", "bone", "rail", "imagine", "provide", "agree", "thus", "capital", "won't", "chair", "danger", "fruit", "rich", "thick", 
    "soldier", "process", "operate", "guess", "necessary", "sharp", "wing", "create", "neighbor", "wash", "bat", "rather", "crowd", 
    "corn", "compare", "poem", "string", "bell", "depend", "meat", "rub", "tube", "famous", "dollar", "stream", "fear", "sight", 
    "thin", "triangle", "planet", "hurry", "chief", "colony", "clock", "mine", "tie", "enter", "major", "fresh", "search", "send", 
    "yellow", "gun", "allow", "print", "dead", "spot", "desert", "suit", "current", "lift", "rose", "continue", "block", "chart", 
    "hat", "sell", "success", "company", "subtract", "event", "particular", "deal", "swim", "term", "opposite", "wife", "shoe", 
    "shoulder", "spread", "arrange", "camp", "invent", "cotton", "born", "determine", "quart", "nine", "truck", "noise", "level", 
    "chance", "gather", "shop", "stretch", "throw", "shine", "property", "column", "molecule", "select", "wrong", "gray", "repeat", 
    "require", "broad", "prepare", "salt", "nose", "plural", "anger", "claim", "continent", "oxygen", "sugar", "death", "pretty", 
    "skill", "women", "season", "solution", "magnet", "silver", "thank", "branch", "match", "suffix", "especially", "fig", "afraid", 
    "huge", "sister", "steel", "discuss", "forward", "similar", "guide", "experience", "score", "apple", "bought", "led", "pitch", 
    "coat", "mass", "card", "band", "rope", "slip", "win", "dream", "evening", "condition", "feed", "tool", "total", "basic", 
    "smell", "valley", "nor", "double", "seat", "arrive", "master", "track", "parent", "shore", "division", "sheet", "substance", 
    "favor", "connect", "post", "spend", "chord", "fat", "glad", "original", "share", "station", "dad", "bread", "charge", "proper", 
    "bar", "offer", "segment", "slave", "duck", "instant", "market", "degree", "populate", "chick", "dear", "enemy", "reply", 
    "drink", "occur", "support", "speech", "nature", "range", "steam", "motion", "path", "liquid", "log", "meant", "quotient", 
    "teeth", "shell", "neck"
]

class KeyboardSignals(QObject):
    press_key_sig = pyqtSignal(str)
    highlight_key_sig = pyqtSignal(str)
    update_suggestions_sig = pyqtSignal(list)
    highlight_suggestion_sig = pyqtSignal(int)
    select_suggestion_sig = pyqtSignal(int)
    close_sig = pyqtSignal()

class ModernKeyboardWindow(QMainWindow):
    def __init__(self, signals, key_layout):
        super().__init__()
        self.signals = signals
        self.key_layout = key_layout
        self.buttons = {}
        self.suggestion_buttons = []
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        # Window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {config.UI_BG_TRANSPARENT};
                border-radius: 20px;
                border: 2px solid {config.UI_BORDER_COLOR};
                font-family: 'Segoe UI';
            }}
            QPushButton {{
                background-color: {config.UI_KEY_DEFAULT};
                color: {config.UI_NEON_BLUE};
                border: 1px solid {config.UI_BORDER_COLOR};
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {config.UI_KEY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {config.UI_KEY_PRESS};
                color: white;
            }}
        """)
        
        # Glow Effect for window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(config.UI_NEON_BLUE))
        shadow.setOffset(0, 0)
        main_widget.setGraphicsEffect(shadow)

        # Suggestions Row
        suggestion_layout = QHBoxLayout()
        for i in range(3):
            btn = QPushButton("")
            btn.setFixedSize(250, 70)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {config.UI_NEON_PURPLE};
                    border: 1px solid {config.UI_NEON_PURPLE};
                    font-size: 20px;
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.on_suggestion_click(idx))
            suggestion_layout.addWidget(btn)
            self.suggestion_buttons.append(btn)
        
        main_layout.addLayout(suggestion_layout)
        
        # Keyboard Layout (Rows)
        keyboard_layout = QVBoxLayout()
        keyboard_layout.setSpacing(10)
        
        for row_keys in self.key_layout:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)
            for key in row_keys:
                btn = QPushButton(key)
                btn.setFixedHeight(85)
                # Let buttons expand width-wise
                btn.setSizePolicy(1, 1) # Expanding, Expanding
                
                btn.clicked.connect(lambda checked, k=key: self.on_key_click(k))
                row_layout.addWidget(btn)
                self.buttons[key] = btn
            keyboard_layout.addLayout(row_layout)
                
        main_layout.addLayout(keyboard_layout)
        
        # Position Right Side
        screen_geo = QApplication.primaryScreen().availableGeometry()
        w, h = 1000, 650
        # Ensure it fits
        x = max(0, screen_geo.width() - w - 50)
        y = max(0, (screen_geo.height() - h) // 2)
        
        self.setGeometry(x, y, w, h)
        self.oldPos = self.pos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def connect_signals(self):
        self.signals.press_key_sig.connect(self.animate_key_press)
        self.signals.highlight_key_sig.connect(self.update_highlight)
        self.signals.update_suggestions_sig.connect(self.update_suggestions_ui)
        self.signals.highlight_suggestion_sig.connect(self.update_suggestion_highlight)
        self.signals.close_sig.connect(self.close)

    def on_key_click(self, key):
        self.signals.press_key_sig.emit(key)
        
    def on_suggestion_click(self, index):
        self.signals.select_suggestion_sig.emit(index)

    def animate_key_press(self, key):
        if key in self.buttons:
            btn = self.buttons[key]
            # Simple visual flash
            btn.setStyleSheet(f"""
                background-color: {config.UI_KEY_PRESS}; 
                color: white; 
                border: 2px solid white;
            """)
            QTimer.singleShot(200, lambda: self.reset_key_style(btn))

    def reset_key_style(self, btn):
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.UI_KEY_DEFAULT};
                color: {config.UI_NEON_BLUE};
                border: 1px solid {config.UI_BORDER_COLOR};
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
    def update_highlight(self, key):
        # Reset all
        for k, btn in self.buttons.items():
            if k != key:
                self.reset_key_style(btn)
        
        # Highlight specific
        if key in self.buttons:
             self.buttons[key].setStyleSheet(f"""
                background-color: {config.UI_KEY_HOVER}; 
                color: white;
                border: 1px solid {config.UI_NEON_BLUE};
            """)

    def update_suggestions_ui(self, suggestions):
        for i, word in enumerate(suggestions):
            if i < len(self.suggestion_buttons):
                self.suggestion_buttons[i].setText(word)

    def update_suggestion_highlight(self, index):
        for i, btn in enumerate(self.suggestion_buttons):
            if i == index:
                 btn.setStyleSheet(f"""
                    background-color: {config.UI_KEY_HOVER};
                    color: white;
                    border: 2px solid {config.UI_NEON_PURPLE};
                """)
            else:
                 btn.setStyleSheet(f"""
                    color: {config.UI_NEON_PURPLE};
                    border: 1px solid {config.UI_NEON_PURPLE};
                    font-size: 16px;
                """)

class VirtualKeyboard:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.keys = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"],
            ["SPACE", "BSPACE", "ENTER"],
        ]
        
        self.current_word = ""
        self.suggestions = ["", "", ""]
        
        self.signals = KeyboardSignals()
        self.app = None
        self.window = None
        self.thread = None

    # --- Connection from UI back to Logic ---
    def _on_ui_key_press(self, key):
        # Trigger same logic as gesture
        self.press_key(key)
        
    def _on_ui_suggestion_click(self, index):
        self.select_suggestion(index)

    def show(self):
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        self.window = ModernKeyboardWindow(self.signals, self.keys)
        
        # Connect UI signals to controller logic
        self.signals.press_key_sig.connect(self._on_ui_key_press)
        self.signals.select_suggestion_sig.connect(self._on_ui_suggestion_click)
        
        self.window.show()
        
        # Start a timer to poll state (to replicate the logic from original Tkinter loop)
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_state)
        self.poll_timer.start(200)
        
        self.update_suggestions()
        self.app.exec_()
        
    def _poll_state(self):
        if self.state_manager.get_state() != StateManager.KEYBOARD:
            self.window.close()
            self.app.quit() # Stop blocking

    def hide(self):
        if self.signals:
            self.signals.close_sig.emit()

    # --- API used by KeyboardController (Thread-Safe via Signals) ---

    def press_key(self, key: str):
        # self.signals.press_key_sig.emit(key) # REMOVED LOOP: UI emits to controller, controller logic runs, then highlight updates?
        # Use visual feedback
        self.highlight_key(key)
        
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
        if not self.current_word:
            self.suggestions = ["", "", ""]
        else:
            matches = [w for w in COMMON_WORDS if w.startswith(self.current_word.lower())]
            self.suggestions = (matches[:3] + ["", "", ""])[:3]
            
        self.signals.update_suggestions_sig.emit(self.suggestions)

    def highlight_key(self, key):
        self.signals.highlight_key_sig.emit(key)

    def highlight_suggestion(self, index):
        self.signals.highlight_suggestion_sig.emit(index)

    def clear_highlight(self):
        self.signals.highlight_key_sig.emit("")
        self.signals.highlight_suggestion_sig.emit(-1)
