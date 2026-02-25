import cv2
import mediapipe as mp
import math
import time

from state.state_manager import StateManager
from ui.virtual_keyboard import VirtualKeyboard
from vision.hand_recognition import HandRecog, Gest, HLabel
import config

class KeyboardGestureController:
    def __init__(self, state_manager: StateManager, keyboard: VirtualKeyboard):
        self.state_manager = state_manager
        self.keyboard = keyboard

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.last_press_time = 0
        self.press_delay = config.KEY_PRESS_DELAY

        self.keys = keyboard.keys
        # We need to account for the suggestion row which pushes keys down.
        # Ideally, we map screen coordinates to UI coordinates more robustly.
        # For now, let's assume the keys start a bit lower.
        
        self.rows = len(self.keys)
        self.cols = max(len(r) for r in self.keys)

    def _distance(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def run(self):
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        window = config.WINDOW_NAME_KEYBOARD
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window, config.CAM_WINDOW_WIDTH, config.CAM_WINDOW_HEIGHT)
        cv2.moveWindow(window, config.CAM_WINDOW_X, config.CAM_WINDOW_Y)
        
        hand_recog = HandRecog(HLabel.MAJOR)

        with self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=config.CONFIDENCE_HAND_DETECTION,
            min_tracking_confidence=config.CONFIDENCE_HAND_TRACKING,
        ) as hands:

            while cap.isOpened():
                if self.state_manager.get_state() != StateManager.KEYBOARD:
                    break

                ok, frame = cap.read()
                if not ok:
                    continue

                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                # --- HUD ---
                cv2.rectangle(frame, (0,0), (640, 50), (0,0,0), -1)
                cv2.putText(frame, "PINCH=Type | V=Enter | PINKY=Space | FIST=BackSp", (10, 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_TEXT, 1)
                            
                # Draw Suggestion Zones
                zone_h = int(h * config.KEYBOARD_SUGGESTION_ZONE_HEIGHT)
                cv2.line(frame, (0, zone_h), (w, zone_h), (255,255,0), 1)
                cv2.putText(frame, "SUGGESTIONS", (10, int(h*0.15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 1)

                hovered_key = None
                hovered_suggestion_idx = -1

                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0] # Assume one hand
                    
                    # Updates for gesture recognition
                    hand_recog.update_hand_result(hand_landmarks)
                    hand_recog.set_finger_state()
                    gesture = hand_recog.get_gesture()
                    
                    lm = hand_landmarks.landmark
                    index_tip = lm[8]
                    thumb_tip = lm[4]
                    
                    x_raw = index_tip.x
                    y_raw = index_tip.y
                    x = int(x_raw * w)
                    y = int(y_raw * h)
                    
                    cv2.circle(frame, (x, y), 6, config.COLOR_READY, -1)
                    
                    # --- GESTURE COMMANDS ---
                    now = time.time()
                    if now - self.last_press_time > self.press_delay:
                        # V (Peace) = ENTER
                        if gesture == Gest.V_GEST:
                            print("[GESTURE] ENTER")
                            self.keyboard.press_key("ENTER")
                            self.last_press_time = now
                            cv2.putText(frame, "ENTER", (x, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, config.COLOR_CLICK, 2)
                        
                        # PINKY = SPACE (Swapped from Backspace)
                        elif gesture == Gest.PINKY:
                             print("[GESTURE] SPACE")
                             self.keyboard.press_key("SPACE")
                             self.last_press_time = now
                             cv2.putText(frame, "SPACE", (x, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, config.COLOR_CLICK, 2)
                        
                        # FIST = BACKSPACE (Swapped from Space)
                        elif gesture == Gest.FIST:
                            print("[GESTURE] BACKSPACE")
                            self.keyboard.press_key("BSPACE")
                            self.last_press_time = now
                            cv2.putText(frame, "BACKSPACE", (x, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, config.COLOR_CLICK, 2)

                    # --- TYPING LOGIC ---
                    # Check if in suggestion zone (top 20%)
                    if y_raw < config.KEYBOARD_SUGGESTION_ZONE_HEIGHT:
                        # 3 zones
                        if x_raw < config.KEYBOARD_SUGGESTION_ZONE_1_X: hovered_suggestion_idx = 0
                        elif x_raw < config.KEYBOARD_SUGGESTION_ZONE_2_X: hovered_suggestion_idx = 1
                        else: hovered_suggestion_idx = 2
                        
                        cv2.putText(frame, f"SUGGEST #{hovered_suggestion_idx+1}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
                        
                        # Pinch to select suggestion
                        dist = self._distance(index_tip, thumb_tip)
                        if dist < config.KEY_HOVER_DISTANCE and (now - self.last_press_time > self.press_delay):
                            self.keyboard.select_suggestion(hovered_suggestion_idx)
                            self.last_press_time = now
                            cv2.putText(frame, "SELECTED!", (x, y+20), cv2.FONT_HERSHEY_SIMPLEX, 1, config.COLOR_CLICK, 2)

                    else:
                        # Keyboard Zone (bottom 80%)
                        # Remap y from 0.2-1.0 to 0.0-1.0 for the keyboard rows
                        # Remap y from zone_height-1.0 to 0.0-1.0 for the keyboard rows
                        eff_y = (y_raw - config.KEYBOARD_SUGGESTION_ZONE_HEIGHT) / (1.0 - config.KEYBOARD_SUGGESTION_ZONE_HEIGHT)
                        if eff_y < 0: eff_y = 0
                        
                        row = int(eff_y * self.rows)
                        
                        if 0 <= row < self.rows:
                            # Dynamic column mapping based on row length (since UI expands keys to fill width)
                            # keys in this row
                            row_keys = self.keys[row]
                            num_keys = len(row_keys)
                            col = int(x_raw * num_keys)
                            
                            if 0 <= col < num_keys:
                                hovered_key = row_keys[col]
                            
                        dist = self._distance(index_tip, thumb_tip)
                        if dist < config.KEY_HOVER_DISTANCE and hovered_key:
                             cv2.circle(frame, (x, y), 10, config.COLOR_CLICK, -1)
                             if now - self.last_press_time > self.press_delay:
                                print(f"[GESTURE KEY] {hovered_key}")
                                self.keyboard.press_key(hovered_key)
                                self.last_press_time = now
                                cv2.putText(frame, f"PRESSED: {hovered_key}", (x+10, y), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.COLOR_CLICK, 2)

                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                
                # Update UI Highlights
                if hovered_suggestion_idx != -1:
                    self.keyboard.highlight_suggestion(hovered_suggestion_idx)
                    self.keyboard.clear_highlight() # clear keys
                elif hovered_key:
                    self.keyboard.highlight_key(hovered_key)
                    self.keyboard.highlight_suggestion(-1) # clear suggestions
                else:
                    self.keyboard.clear_highlight()
                    self.keyboard.highlight_suggestion(-1)

                cv2.imshow(window, frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        self.keyboard.clear_highlight()
        cap.release()
        cv2.destroyAllWindows()