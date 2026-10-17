import cv2
from core.vision import VisionPipeline
from core.gestures import GestureEngine
from core.controller import SystemController
from utils.smoothing import GestureStabilizer

def main():
    print("Starting Professional Hand Control System...")
    try:
        # Initialize all components
        pipeline = VisionPipeline()
        engine = GestureEngine()
        controller = SystemController()
        stabilizer = GestureStabilizer(required_frames=3)
        print("Systems initialized successfully!")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        print("System Active. Press 'q' to quit.")
        
        last_executed_gesture = "UNKNOWN"
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break
            
            # 1. Vision Pipeline
            processed_frame, hand_data = pipeline.process_frame(frame)
            
            # 2. Gesture Engine
            if hand_data:
                for hand_landmarks in hand_data:
                    # Now returns a tuple: (gesture, data)
                    raw_gesture, data = engine.recognize_gesture(hand_landmarks)
                    
                    # 3. Apply Stabilization
                    # Bypass stabilizer for swipes to ensure instant response to fast motion
                    if "SWIPE" in raw_gesture:
                        stable_gesture = raw_gesture
                    else:
                        stable_gesture = stabilizer.stabilize(raw_gesture)

                    # 4. Execute Action
                    if stable_gesture != "STABILIZING..." and stable_gesture != last_executed_gesture:
                        controller.execute_action(stable_gesture, data)
                        last_executed_gesture = stable_gesture
                    
                    # Volume control is an exception: it's continuous, not a state change
                    if raw_gesture == "VOLUME_CONTROL":
                        controller.execute_action("VOLUME_CONTROL", data)
                    
                    # UI feedback
                    color = (0, 255, 0) if stable_gesture != "STABILIZING..." else (0, 255, 255)
                    cv2.putText(processed_frame, f"Raw: {raw_gesture}", (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                    cv2.putText(processed_frame, f"Stable: {stable_gesture}", (10, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    if data:
                        cv2.putText(processed_frame, f"Dist: {data:.3f}", (10, 110), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)
            else:
                last_executed_gesture = "UNKNOWN"
            
            cv2.imshow('Professional Hand Control', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        print("System shutdown.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
