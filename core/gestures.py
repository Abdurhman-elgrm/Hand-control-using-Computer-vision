import numpy as np
from collections import deque

class GestureEngine:
    def __init__(self):
        self.state = "IDLE"
        self.wrist_buffer = deque(maxlen=15)
        self.threshold_pinch = 0.05
        self.threshold_swipe = 0.1

    def get_distance(self, p1, p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def detect_static(self, landmarks):
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        if self.get_distance(thumb_tip, index_tip) < self.threshold_pinch:
            return "PINCH"
        
        # Check if all fingers are closed (tip is lower than the middle joint)
        # MediaPipe Y increases as you go down
        is_fist = all(landmarks[i][1] > landmarks[i-2][1] for i in [8, 12, 16, 20])
        if is_fist: 
            return "FIST"
        return None

    def detect_dynamic(self, landmarks):
        wrist = landmarks[0]
        self.wrist_buffer.append(wrist[0])
        if len(self.wrist_buffer) == self.wrist_buffer.maxlen:
            diff = self.wrist_buffer[-1] - self.wrist_buffer[0]
            if diff > self.threshold_swipe: 
                return "SWIPE_RIGHT"
            if diff < -self.threshold_swipe: 
                return "SWIPE_LEFT"
        return None

    def recognize_gesture(self, landmarks):
        """
        Unified entry point for gesture recognition.
        """
        # Priority: Static gestures (like pinch/fist) first, then dynamic (swipes)
        gesture = self.detect_static(landmarks) or self.detect_dynamic(landmarks)
        return gesture if gesture else "UNKNOWN"
