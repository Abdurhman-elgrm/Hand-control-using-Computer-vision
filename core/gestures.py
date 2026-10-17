import numpy as np
from collections import deque
import time
from utils.config import ConfigManager

class GestureEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.motion_buffer = deque(maxlen=5)
        self.last_action_time = 0
        self.cooldown_duration = 0.5  # seconds

        # Load thresholds from config
        self.threshold_swipe_velocity = self.config.get("swipe_velocity_threshold", 0.005) # Lowered from 0.015 for higher sensitivity

    def get_palm_centroid(self, landmarks):
        # Landmarks for the palm: wrist, base of fingers
        palm_indices = [0, 5, 9, 13, 17]
        points = np.array([landmarks[i] for i in palm_indices])
        return np.mean(points, axis=0)

    def detect_dynamic(self, landmarks):
        current_time = time.time()
        if current_time - self.last_action_time < self.cooldown_duration:
            return None

        centroid = self.get_palm_centroid(landmarks)
        self.motion_buffer.append(centroid[0])

        if len(self.motion_buffer) < self.motion_buffer.maxlen:
            return None

        # Calculate average velocity (change per frame)
        total_diff = self.motion_buffer[-1] - self.motion_buffer[0]
        avg_velocity = total_diff / len(self.motion_buffer)

        if avg_velocity > self.threshold_swipe_velocity:
            self.last_action_time = current_time
            self.motion_buffer.clear()
            return "SWIPE_RIGHT"
        elif avg_velocity < -self.threshold_swipe_velocity:
            self.last_action_time = current_time
            self.motion_buffer.clear()
            return "SWIPE_LEFT"

        return None

    def recognize_gesture(self, landmarks):
        gesture = self.detect_dynamic(landmarks)
        return gesture if gesture else "UNKNOWN", None
