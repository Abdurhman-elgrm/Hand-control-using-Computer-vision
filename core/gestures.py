import numpy as np
from collections import deque
from utils.config import ConfigManager

class GestureEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.state = "IDLE"
        self.wrist_buffer = deque(maxlen=5)
        
        # Load thresholds from config
        self.threshold_pinch = self.config.get("pinch_threshold", 0.04)
        self.threshold_swipe = self.config.get("swipe_threshold", 0.04)

    def get_distance(self, p1, p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def detect_static(self, landmarks):
        # --- PRIORITY 1: FIST ---
        is_fist = all(landmarks[i][1] > landmarks[i-2][1] + 0.01 for i in [8, 12, 16, 20])
        if is_fist:
            return "FIST"

        # --- PRIORITY 2: OPEN PALM ---
        is_palm = all(landmarks[i][1] < landmarks[i-2][1] for i in [8, 12, 16, 20])
        if is_palm:
            return "OPEN_PALM"

        # --- PRIORITY 3: PEACE sign ---
        if (landmarks[8][1] < landmarks[6][1] and
            landmarks[12][1] < landmarks[10][1] and
            landmarks[16][1] > landmarks[14][1] and
            landmarks[20][1] > landmarks[18][1]):
            return "PEACE"

        # --- PRIORITY 4: VOLUME/PINCH ---
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        dist = self.get_distance(thumb_tip, index_tip)
        
        if 0.05 < dist < 0.15:
            return "VOLUME_CONTROL"

        return None

    def detect_dynamic(self, landmarks):
        # To prevent conflict with OPEN_PALM, we only track swipes 
        # if the hand is NOT in a perfect open palm state.
        # If it's an open palm, we treat it as a static gesture unless 
        # the movement is very aggressive.
        
        # Check if it's an open palm
        is_palm = all(landmarks[i][1] < landmarks[i-2][1] for i in [8, 12, 16, 20])
        
        palm_center = landmarks[9]
        self.wrist_buffer.append(palm_center[0])

        if len(self.wrist_buffer) < self.wrist_buffer.maxlen:
            return None

        diff = self.wrist_buffer[-1] - self.wrist_buffer[0]

        # If it's a palm, we require a MUCH stronger movement to trigger a swipe
        # This prevents a slightly moving open palm from being seen as a swipe.
        current_threshold = self.threshold_swipe * 2 if is_palm else self.threshold_swipe

        if diff > current_threshold:
            self.wrist_buffer.clear()
            return "SWIPE_RIGHT"
        elif diff < -current_threshold:
            self.wrist_buffer.clear()
            return "SWIPE_LEFT"

        return None

    def recognize_gesture(self, landmarks):
        # CRITICAL CHANGE: Static first, then Dynamic.
        # This means if the hand is a clear "OPEN PALM", it will be 
        # recognized as a palm even if it's moving slightly.
        # A swipe will only trigger if the hand is NOT a palm, or if it's moving very fast.
        gesture = self.detect_static(landmarks) or self.detect_dynamic(landmarks)
        
        data = None
        if gesture == "VOLUME_CONTROL":
            data = self.get_distance(landmarks[4], landmarks[8])
            
        return gesture if gesture else "UNKNOWN", data
