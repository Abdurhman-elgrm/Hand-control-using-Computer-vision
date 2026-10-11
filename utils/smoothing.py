import numpy as np
from collections import deque

class SmoothingFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)

    def apply(self, value):
        """
        Applies a moving average filter to smooth out jittery input.
        """
        self.buffer.append(value)
        return np.mean(self.buffer)

class GestureStabilizer:
    def __init__(self, required_frames=3):
        self.required_frames = required_frames
        self.history = deque(maxlen=required_frames)

    def stabilize(self, gesture):
        """
        Returns the gesture only if it has been consistent for X frames.
        This prevents 'flickering' between gestures.
        """
        self.history.append(gesture)
        if len(self.history) == self.required_frames and len(set(self.history)) == 1:
            return gesture
        return "STABILIZING..."
