import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class VisionPipeline:
    def __init__(self, model_path="hand_landmarker.task"):
        # Initialize the Hand Landmarker using the new Tasks API
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def process_frame(self, frame):
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect landmarks
        detection_result = self.detector.detect(mp_image)
        
        hand_data = []
        
        if detection_result.hand_landmarks:
            for landmarks_list in detection_result.hand_landmarks:
                # Convert landmarks to a list of (x, y, z) tuples
                landmarks = [(lm.x, lm.y, lm.z) for lm in landmarks_list]
                hand_data.append(landmarks)
                
                # Draw landmarks on the frame
                h, w, _ = frame.shape
                for lm in landmarks_list:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)

        return frame, hand_data
