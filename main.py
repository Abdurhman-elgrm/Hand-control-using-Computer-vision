import cv2
from core.vision import VisionPipeline

def main():
    print("Starting Vision Test...")
    try:
        pipeline = VisionPipeline()
        print("Vision Pipeline initialized successfully!")
        
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
            
            # Process the frame using our pipeline
            processed_frame, hand_data = pipeline.process_frame(frame)
            
            # Display data on screen for testing
            if hand_data:
                print(f"Hands detected: {len(hand_data)}")
            
            cv2.imshow('Vision Test', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        print("Test finished.")

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()
