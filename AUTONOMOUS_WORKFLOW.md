# 🌌 Autonomous Spatial Control System (ASCS) - Master Workflow & Learning Guide

This document is your technical roadmap. It contains the blueprints for the system. **The goal is for you to implement these skeletons to learn the professional architecture.**

---

## 🛠 Phase 1: The Core Infrastructure (The Engine)
*Focus: Multithreading and Smoothness.*

### 1.1 Event-Driven Architecture (The Skeleton)
Instead of one loop, we use `threading` and `queue` to ensure the camera never lags when a key is pressed.

**Code Blueprint:**
```python
import threading
import queue
import time

class ASCS_Engine:
    def __init__(self):
        # Queue for landmarks from Vision -> Analysis
        self.vision_queue = queue.Queue(maxsize=1)
        # Queue for commands from Analysis -> Execution
        self.action_queue = queue.Queue()
        self.running = True

    def vision_worker(self):
        """Captures frames and extracts landmarks"""
        while self.running:
            # 1. Capture frame
            # 2. Get landmarks via VisionPipeline
            # 3. Put into queue (use block=False to avoid lag)
            # self.vision_queue.put(landmarks, block=False)
            pass

    def analysis_worker(self):
        """Turns landmarks into Intent/Actions"""
        while self.running:
            # 1. Get landmarks from self.vision_queue
            # 2. Determine Zone (Phase 2) or Gesture (Phase 4)
            # 3. Put the action into self.action_queue
            # self.action_queue.put("SWIPE_LEFT")
            pass

    def execution_worker(self):
        """Triggers the OS actions"""
        while self.running:
            # 1. Get action from self.action_queue
            # 2. Trigger PyAutoGUI via SystemController
            pass

    def start(self):
        """Launches the threads"""
        # Create threading.Thread for each worker
        # Start them and keep main thread alive
        pass
```

### 1.2 The Air-Mouse (The Logic)
**How to implement the smoothing:**
To stop the cursor from shaking, use a **Low-Pass Filter**:
$\text{smoothed\_pos} = (\text{previous\_pos} \times 0.8) + (\text{current\_pos} \times 0.2)$

*   **Pro Tip**: Lowering the `0.2` (e.g., to `0.1`) makes it smoother but slower. Increasing it makes it snappier but more jittery.

---

## 🗺 Phase 2: Spatial Mapping (The 3D Surface)
*Focus: Turning the camera view into a control panel.*

### 2.1 The Zone Manager (The Skeleton)
**Code Blueprint:**
```python
class ZoneManager:
    def __init__(self):
        # Define X-axis boundaries (0.0 to 1.0)
        self.zones = {
            "LEFT_UTILITY": (0.0, 0.2),   
            "COMMAND_CENTER": (0.2, 0.8), 
            "RIGHT_UTILITY": (0.8, 1.0),  
        }

    def get_zone(self, centroid_x):
        """Checks which range the hand x-coordinate falls into"""
        # TASK: loop through self.zones and check if 
        # min_x <= centroid_x <= max_x
        # return zone_name
        pass
```

---

## 🎭 Phase 3: Contextual Mode Management (The Brain)
*Focus: One hand, many different tools.*

### 3.1 Mode Controller (The Skeleton)
**Code Blueprint:**
```python
class ModeController:
    def __init__(self):
        self.current_mode = "MEDIA" # Options: MEDIA, WORK, PRESENTATION
        self.mode_map = {
            "MEDIA": {"SWIPE_RIGHT": "next_video", "PINCH": "volume"},
            "WORK": {"SWIPE_RIGHT": "next_desktop", "PINCH": "minimize"},
        }

    def switch_mode(self, trigger_gesture):
        """Switches mode if a specific gesture (like PEACE) is held"""
        # TASK: If trigger_gesture == "PEACE", cycle to next mode
        pass

    def get_action(self, gesture):
        """Returns the specific action based on the current active mode"""
        # TASK: return self.mode_map[self.current_mode].get(gesture)
        pass
```

---

## 🧠 Phase 4: Complex Motion AI (The Intelligence)
*Focus: Moving from "Triggers" to "Patterns".*

### 4.1 The Data Collector (The Skeleton)
**Code Blueprint:**
```python
class DataCollector:
    def record_session(self, gesture_label):
        """Records a sequence of movements to a CSV file"""
        # TASK: 
        # 1. While recording: append [frame_id, x, y, z] to a list
        # 2. When stopped: use pandas or csv module to save to file
        # Example: "circle_gesture_1.csv"
        pass
```

### 4.2 The AI Predictor (The Logic)
**Implementation Path:**
1. **Data**: Use a sliding window of 30 frames of landmarks.
2. **Model**: LSTM (Long Short-Term Memory) $\rightarrow$ Dense $\rightarrow$ Softmax.
3. **Inference**: `model.predict(window)` $\rightarrow$ if prob $> 0.9 \rightarrow$ Action.

---

## 🏁 Your Learning Path (Task List)

1. [ ] **Task 1**: Set up the `ASCS_Engine` threading. (Verify: FPS stays constant during actions).
2. [ ] **Task 2**: Implement the `Air-Mouse` smoothing. (Verify: Cursor moves without shaking).
3. [ ] **Task 3**: Implement the `ZoneManager`. (Verify: Different actions on screen edges).
4. [ ] **Task 4**: Build the `ModeController`. (Verify: Peace sign changes app behavior).
5. [ ] **Task 5**: Build the `DataCollector` and train a simple LSTM for one custom gesture.
