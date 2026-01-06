
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
