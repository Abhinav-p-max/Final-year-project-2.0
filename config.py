
# ================= CONFIGURATION =================

# Camera & Display
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
WINDOW_NAME_MOUSE = "Voice & Gesture - Mouse Mode"
WINDOW_NAME_KEYBOARD = "Voice & Gesture - Keyboard Mode"

# Mouse Control
# Smoothing factor (0.0 to 1.0). Lower = smoother but more lag. Higher = faster but jittery.
MOUSE_SMOOTHING = 0.5 
MOUSE_SENSITIVITY = 2.0 # Multiplier for hand movement to screen movement

# Gesture Thresholds
CONFIDENCE_HAND_DETECTION = 0.7
CONFIDENCE_HAND_TRACKING = 0.6
CLICK_DEBOUNCE_TIME = 0.3

# Virtual Keyboard
KEY_PRESS_DELAY = 1.0     # Function: Seconds to hover before pressing
KEY_HOVER_DISTANCE = 0.05 # Distance between index and thumb to trigger press

# Visuals (BGR format for OpenCV)
COLOR_TEXT = (255, 255, 255)       # White
COLOR_READY = (0, 255, 0)          # Green
COLOR_ACTIVE = (0, 165, 255)       # Orange
COLOR_CLICK = (0, 0, 255)          # Red
FONT = 1 # cv2.FONT_HERSHEY_SIMPLEX (Using int to avoid importing cv2 here if not needed)

# Keyboard Vision Limits
KEYBOARD_SUGGESTION_ZONE_HEIGHT = 0.2
KEYBOARD_SUGGESTION_ZONE_1_X = 0.33
KEYBOARD_SUGGESTION_ZONE_2_X = 0.66
KEY_HOVER_DISTANCE = 0.05

# Camera Window Geometry
CAM_WINDOW_WIDTH = 300
CAM_WINDOW_HEIGHT = 220
CAM_WINDOW_X = 0
CAM_WINDOW_Y = 600

# UI Aesthetics
UI_BG_COLOR = "#2b2b2b"       # Dark Grey
UI_FG_COLOR = "#ffffff"       # White
UI_KEY_BG = "#444444"         # Lighter Grey
UI_KEY_FG = "#ffffff"
UI_HIGHLIGHT_BG = "#00adb5"   # Cyan/Teal
UI_SUGGESTION_BG = "#393e46"  # Medium Grey
UI_FONT_MAIN = ("Segoe UI", 12, "bold")
UI_FONT_SUGGESTION = ("Segoe UI", 12, "bold")

# Futuristic UI (PyQt)
UI_NEON_BLUE = "#00f3ff"
UI_NEON_PURPLE = "#bc13fe"
UI_BG_TRANSPARENT = "rgba(10, 10, 20, 200)" # Dark subtle blue-black
UI_KEY_DEFAULT = "rgba(255, 255, 255, 10)"
UI_KEY_HOVER = "rgba(0, 243, 255, 50)"
UI_KEY_PRESS = "rgba(0, 243, 255, 150)"
UI_BORDER_COLOR = "rgba(0, 243, 255, 100)"

