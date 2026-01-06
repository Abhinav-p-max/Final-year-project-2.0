import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import time

from state.state_manager import StateManager
from vision.hand_recognition import HandRecog, Gest, HLabel
import config

pyautogui.FAILSAFE = False

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# ===================== CONTROLLER =====================

class Controller:
    # Smoothing State
    prev_screen_x, prev_screen_y = 0, 0
    curr_screen_x, curr_screen_y = 0, 0
    
    # Drag state
    grabflag = False
    
    # Click state
    last_click_time = 0

    @staticmethod
    def get_position(hand_result):
        """
        Calculates screen coordinates from hand landmarks with Smoothing.
        """
        point = 9 # Middle finger knuckle usually stable
        
        # Get frame coordinates
        raw_x = hand_result.landmark[point].x
        raw_y = hand_result.landmark[point].y

        # Screen dimensions
        sx, sy = pyautogui.size()

        # Map frame coordinates (0-1) to screen coordinates.
        # We start by just scaling, but usually we need a mapping to allow reaching corners.
        # For simplicity in this iteration, we keep the previous relative logic but smoothed.
        
        # Current logic in original code was delta-based relative to mouse position.
        # Let's switch to absolute mapping for better predictability, or improve the delta logic.
        # Preserving the user's "delta" approach but smoothing the INPUT first.
        
        target_x = int(raw_x * sx)
        target_y = int(raw_y * sy)
        
        # Initialize if zero
        if Controller.prev_screen_x == 0 and Controller.prev_screen_y == 0:
            Controller.prev_screen_x = target_x
            Controller.prev_screen_y = target_y
            return pyautogui.position() # No move first frame

        # Smoothing Formula:
        # Current = Alpha * Target + (1 - Alpha) * Previous
        alpha = config.MOUSE_SMOOTHING
        
        Controller.curr_screen_x = alpha * target_x + (1 - alpha) * Controller.prev_screen_x
        Controller.curr_screen_y = alpha * target_y + (1 - alpha) * Controller.prev_screen_y
        
        # Calculate Delta from our internal smoothed tracker
        delta_x = Controller.curr_screen_x - Controller.prev_screen_x
        delta_y = Controller.curr_screen_y - Controller.prev_screen_y
        
        # Update previous
        Controller.prev_screen_x = Controller.curr_screen_x
        Controller.prev_screen_y = Controller.curr_screen_y
        
        # Apply Sensitivity
        delta_x *= config.MOUSE_SENSITIVITY
        delta_y *= config.MOUSE_SENSITIVITY
        
        # Get current actual mouse pos to add delta
        curr_mouse_x, curr_mouse_y = pyautogui.position()
        final_x = curr_mouse_x + delta_x
        final_y = curr_mouse_y + delta_y

        return final_x, final_y

    @staticmethod
    def handle_controls(gesture, hand_result, image):
        """
        Executes mouse actions based on gesture and draws feedback on the image.
        """
        x, y = pyautogui.position()
        status_text = "Tracking"
        
        if gesture != Gest.PALM:
            x, y = Controller.get_position(hand_result)
        
        # Logic
        if gesture != Gest.FIST and Controller.grabflag:
            Controller.grabflag = False
            pyautogui.mouseUp()

        if gesture == Gest.INDEX:
            status_text = "MOVING"
            pyautogui.moveTo(x, y, duration=0) # Duration 0 for instant response (smoothing handles the rest)

        elif gesture == Gest.FIST:
            status_text = "DRAGGING / HOLD"
            if not Controller.grabflag:
                Controller.grabflag = True
                pyautogui.mouseDown()
            pyautogui.moveTo(x, y, duration=0)

        elif gesture == Gest.V_GEST:
            status_text = "CLICK"
            if time.time() - Controller.last_click_time > config.CLICK_DEBOUNCE_TIME:
                pyautogui.click()
                Controller.last_click_time = time.time()

        elif gesture == Gest.ROCK_GEST:
            status_text = "RIGHT CLICK"
            if time.time() - Controller.last_click_time > config.CLICK_DEBOUNCE_TIME:
                pyautogui.rightClick()
                Controller.last_click_time = time.time()
            
        elif gesture == Gest.PALM:
            status_text = "PAUSED (Clutch)"
            # Reset smoothing to prevent jump when resuming
            Controller.prev_screen_x = 0
            Controller.prev_screen_y = 0
            
        # --- UI Feedback ---
        cv2.putText(image, f"Status: {status_text}", (10, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.COLOR_ACTIVE, 2)
        
        if gesture == Gest.FIST:
             cv2.circle(image, (50, 80), 10, config.COLOR_CLICK, -1)
        elif gesture == Gest.ROCK_GEST:
             cv2.circle(image, (50, 80), 10, config.COLOR_CLICK, -1)


# ===================== MAIN RUNNER =====================

class MouseController:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def classify_hands(self, results):
        left = None
        right = None

        for i, hand in enumerate(results.multi_hand_landmarks):
            label = results.multi_handedness[i].classification[0].label
            if label == "Right":
                right = hand
            else:
                left = hand

        return right, left

    def run(self):
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        
        Controller.prev_screen_x = 0 # Reset smoothing
        Controller.prev_screen_y = 0

        handmajor = HandRecog(HLabel.MAJOR)

        with mp_hands.Hands(
            max_num_hands=1, # Limit to 1 for mouse control to avoid confusion
            min_detection_confidence=config.CONFIDENCE_HAND_DETECTION,
            min_tracking_confidence=config.CONFIDENCE_HAND_TRACKING
        ) as hands:

            while cap.isOpened():

                if self.state_manager.get_state() != StateManager.MOUSE:
                    break

                success, image = cap.read()
                if not success:
                    continue

                image = cv2.flip(image, 1)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)
                
                # --- HUD ---
                cv2.rectangle(image, (0,0), (640, 40), (0,0,0), -1)
                cv2.putText(image, "Mouse: INDEX(Move) FIST(Drag) V(Click) ROCK(R-Click) PALM(Pause)", (10, 25), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_TEXT, 1)
                
                if results.multi_hand_landmarks:
                    right, left = self.classify_hands(results)

                    # Prioritize Right hand for mouse (or just the detected one if 1 hand max)
                    target_hand = right if right else (results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None)

                    if target_hand:
                        handmajor.update_hand_result(target_hand)
                        handmajor.set_finger_state()
                        gest = handmajor.get_gesture()
                        
                        # Pass image for drawing feedback inside controller
                        Controller.handle_controls(gest, target_hand, image) 
                        
                        mp_drawing.draw_landmarks(
                            image, target_hand, mp_hands.HAND_CONNECTIONS
                        )
                else:
                    # Reset dragging if hand lost
                    if Controller.grabflag:
                       Controller.grabflag = False
                       pyautogui.mouseUp()

                cv2.imshow(config.WINDOW_NAME_MOUSE, image)
                
                # Exit on Q or specific key (State manager handles global exit usually)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.state_manager.set_state(StateManager.IDLE)
                    break

        cap.release()
        cv2.destroyAllWindows()
