# 🖐️ Advanced Hand Control System Workflow

This document serves as the architectural blueprint for building a professional, hybrid hand-control system using Computer Vision.

## 🎯 Project Objective
Create a system that translates hand landmarks into system-level commands (Keyboard/Mouse) using a **Hybrid Recognition Engine** (Static Shapes + Dynamic Motion) with a **State Machine** to prevent accidental triggers.

---

## 🛠️ Technical Stack
- **Language:** Python 3.10+
- **Vision:** `OpenCV` (Image processing), `MediaPipe` (Hand landmark extraction)
- **System Control:** `PyAutoGUI` or `Pynput` (Virtual key presses)
- **Configuration:** `YAML` or `JSON` (For mapping gestures to keys)
- **Optimization:** `NumPy` (Vector math for distance/angles)

---

## 🗺️ Implementation Roadmap

### Phase 1: The Vision Pipeline (Foundation)
**Goal:** Get a stable stream of hand landmarks.
- [ ] **Camera Setup:** Implement a robust OpenCV video capture loop.
- [ ] **Landmark Extraction:** Integrate MediaPipe Hands to get 21 3D coordinates per hand.
- [ ] **Coordinate Normalization:** Convert absolute pixel coordinates to relative coordinates (0.0 to 1.0) so the system works regardless of how far you are from the camera.

#### 💡 Phase 1 Learning Guide & Pseudocode
**What to learn here:**
- How to handle real-time video frames with OpenCV.
- Understanding the MediaPipe `Hands` solution.
- The difference between `landmark` (relative) and `pixel` (absolute) coordinates.

**Implementation Guide for `core/vision.py`:**
1. **Create a `VisionPipeline` class.**
2. **Initialize MediaPipe:** In `__init__`, set up `mp.solutions.hands.Hands` with parameters like `static_image_mode=False` (since we are using video) and `max_num_hands=2`.
3. **The Process Loop:**
    - Capture frame $\rightarrow$ Convert BGR (OpenCV) to RGB (MediaPipe).
    - Process the frame to get `results`.
    - If `results.multi_hand_landmarks` exists, iterate through them.
4. **Data Extraction:** Create a method that extracts the $(x, y, z)$ of each landmark into a clean Python list or NumPy array.
5. **Visualization:** Use `mp.solutions.drawing_utils` to draw the landmarks on the frame for debugging.

**💻 Code Reference (Phase 1):**
```python
import cv2
import mediapipe as mp

class VisionPipeline:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, 
            max_num_hands=2, 
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        hand_data = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append((lm.x, lm.y, lm.z))
                hand_data.append(landmarks)
        return frame, hand_data
```

### Phase 2: The Hybrid Gesture Engine (The "Brain")
**Goal:** Translate landmarks into "Gestures."
- [ ] **Static Detection:**
    - Implement distance-based logic (e.g., if distance between index tip and thumb tip < threshold $\rightarrow$ "Pinch").
    - Implement finger-state logic (Up/Down) using landmark Y-coordinates.
- [ ] **Dynamic Detection (Motion):**
    - Implement a **Buffer (Queue)** to store the last 10-20 frames of landmark positions.
    - Calculate the delta ($\Delta$) of the wrist or palm center to detect "Swipes" (Left, Right, Up, Down).
- [ ] **Hybrid State Machine:**
    - **IDLE:** System is watching but doing nothing.
    - **ACTIVATION:** A specific "Wake" gesture is detected.
    - **COMMAND:** The system is now actively mapping gestures to actions.

#### 💡 Phase 2 Learning Guide & Pseudocode
**What to learn here:**
- **Distance Formula:** Using Euclidean distance to check if two points are "touching."
- **Temporal Buffering:** Using `collections.deque` to store a history of movement.
- **State Management:** Creating a system that only triggers actions when "Armed."

**Implementation Guide for `core/gestures.py`:**
1. **The Math Helper:** Create a function `get_distance(p1, p2)` that calculates the distance between two $(x,y)$ points.
2. **Static Logic:**
    - **Pinch:** Distance between Landmark 4 (Thumb Tip) and 8 (Index Tip) < 0.05.
    - **Fist:** All finger tips (8, 12, 16, 20) are below their respective knuckles.
3. **Dynamic Logic:**
    - Store the `x` coordinate of Landmark 0 (Wrist) in a `deque(maxlen=15)`.
    - If `current_x - first_x_in_buffer > threshold` $\rightarrow$ "Swipe Right."
4. **State Machine:** Implement a variable `self.state` (e.g., `"IDLE"` or `"ACTIVE"`). Only return a gesture if `self.state == "ACTIVE"`.

**💻 Code Reference (Phase 2):**
```python
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
        is_fist = all(landmarks[i][1] > landmarks[i-2][1] for i in [8, 12, 16, 20])
        if is_fist: return "FIST"
        return None

    def detect_dynamic(self, landmarks):
        wrist = landmarks[0]
        self.wrist_buffer.append(wrist[0])
        if len(self.wrist_buffer) == self.wrist_buffer.maxlen:
            diff = self.wrist_buffer[-1] - self.wrist_buffer[0]
            if diff > self.threshold_swipe: return "SWIPE_RIGHT"
            if diff < -self.threshold_swipe: return "SWIPE_LEFT"
        return None

    def update(self, landmarks):
        gesture = self.detect_static(landmarks) or self.detect_dynamic(landmarks)
        return gesture
```

### Phase 3: System Integration (The "Hands")
**Goal:** Make the computer actually do things.
- [ ] **Command Pattern:** Create a `Controller` class that maps a `GestureName` to a `SystemAction`.
- [ ] **App Specifics:**
    - *YouTube:* Map "Fist" $\rightarrow$ `pyautogui.press('space')`.
    - *Screenshots:* Map "Peace Sign" $\rightarrow$ `pyautogui.hotkey('win', 'shift', 's')`.
- [ ] **Configuration File:** Move all mappings to a `config.yaml` so you can change keys without restarting the code.

#### 💡 Phase 3 Learning Guide & Pseudocode
**What to learn here:**
- **Virtual Input:** How to send keystrokes to Windows.
- **Config-Driven Development:** Separating "what happens" from "how it's detected."

**Implementation Guide for `core/controller.py`:**
1. **The Controller Class:** Create a class that takes the `config.yaml` mapping.
2. **The Execution Method:** `execute(gesture_name)` $\rightarrow$ looks up the key in config $\rightarrow$ calls `pyautogui.press()`.
3. **Integration:** In `main.py`, if `GestureEngine` returns a gesture, pass it to `Controller.execute()`.

**💻 Code Reference (Phase 3):**
```python
import pyautogui
import yaml

class SystemController:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, 'r') as f:
            self.mappings = yaml.safe_load(f)

    def execute(self, gesture):
        if gesture in self.mappings:
            keys = self.mappings[gesture]
            if isinstance(keys, list):
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(keys)
            print(f"Executed: {gesture} -> {keys}")
```

### Phase 4: Advanced Optimization (The "Polish")
**Goal:** Remove jitter and improve UX.
- [ ] **Smoothing:** Implement a **Moving Average Filter** or **Kalman Filter** on coordinates to stop the cursor/action from shaking.
- [ ] **Visual Feedback:** Draw the landmarks and the *current detected gesture name* on the OpenCV window.
- [ ] **Dead-zones:** Implement a central "neutral zone" where no movement is registered to avoid drifting.

---

## 📐 Architectural Design

### Data Flow
`Camera` $\rightarrow$ `MediaPipe` $\rightarrow$ `Landmark Normalizer` $\rightarrow$ `Gesture Logic` $\rightarrow$ `State Machine` $\rightarrow$ `System Controller` $\rightarrow$ `Windows OS`

### Key Mathematical Concepts to Use
1. **Euclidean Distance:** $\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ (To detect pinches/fists).
2. **Angle Calculation:** Use `atan2` to determine the orientation of the hand.
3. **Centroid Tracking:** Average the positions of all landmarks to track the hand's global movement.
