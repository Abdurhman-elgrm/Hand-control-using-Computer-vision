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
        # To avoid conflict with volume control, we make the Fist detection more strict.
        # Tips must be clearly below the PIP joints.
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
        
        # Tightened the volume range to avoid overlap with a closed fist.
        # If dist is very small (< 0.03), it's likely a tight pinch/fist.
        if 0.05 < dist < 0.15:
            return "VOLUME_CONTROL"

        return None

    def detect_dynamic(self, landmarks):
        palm_center = landmarks[9]
        self.wrist_buffer.append(palm_center[0])

        if len(self.wrist_buffer) < self.wrist_buffer.maxlen:
            return None

        diff = self.wrist_buffer[-1] - self.wrist_buffer[0]

        if diff > self.threshold_swipe:
            self.wrist_buffer.clear()
            return "SWIPE_RIGHT"
        elif diff < -self.threshold_swipe:
            self.wrist_buffer.clear()
            return "SWIPE_LEFT"

        return None

    def recognize_gesture(self, landmarks):
        gesture = self.detect_dynamic(landmarks) or self.detect_static(landmarks)
        
        data = None
        if gesture == "VOLUME_CONTROL":
            data = self.get_distance(landmarks[4], landmarks[8])
            
        return gesture if gesture else "UNKNOWN", data
