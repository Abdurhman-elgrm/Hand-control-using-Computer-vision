import cv2
from core.vision import VisionPipeline
from core.gestures import GestureEngine

def main():
    print("Starting Gesture Test...")
    try:
        pipeline = VisionPipeline()
        engine = GestureEngine()
        print("Systems initialized successfully!")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        print("Press 'q' to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break
            
            # 1. Get landmarks from vision pipeline
            processed_frame, hand_data = pipeline.process_frame(frame)
            
            # 2. Process gestures for each detected hand
            if hand_data:
                for hand_landmarks in hand_data:
                    gesture = engine.recognize_gesture(hand_landmarks)
                    
                    # Display the gesture name on the screen
                    cv2.putText(processed_frame, f"Gesture: {gesture}", (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    print(f"Detected: {gesture}")
            
            cv2.imshow('Gesture Test', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        print("Test finished.")

    except Exception as e:
        print(f"An error occurred during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
