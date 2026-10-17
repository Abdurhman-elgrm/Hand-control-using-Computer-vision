import pyautogui
import time
from utils.config import ConfigManager

class SystemController:
    def __init__(self):
        self.config = ConfigManager()
        pyautogui.FAILSAFE = True
        # Track the previous distance to see if the volume is moving UP or DOWN
        self.prev_dist = None

    def execute_action(self, gesture, data=None):
        """
        Maps a recognized gesture to a specific system action using config.yaml.
        """
        if gesture == "VOLUME_CONTROL":
            if data is not None:
                # Calculate the change in distance since last frame
                if self.prev_dist is not None:
                    diff = data - self.prev_dist
                    
                    # Sensitivity threshold to avoid accidental tiny movements
                    sensitivity = 0.005 
                    
                    if diff > sensitivity:
                        # Distance increased -> Volume Up
                        pyautogui.press('volumeup')
                    elif diff < -sensitivity:
                        # Distance decreased -> Volume Down
                        pyautogui.press('volumedown')
                
                self.prev_dist = data
            return

        actions = self.config.get("actions", {})
        action = actions.get(gesture)

        if not action:
            return

        print(f"Executing Action for {gesture}: {action}")

        if action == "space":
            pyautogui.keyDown('space')
            time.sleep(0.1)
            pyautogui.keyUp('space')
        elif action == "volumedown":
            pyautogui.press('volumedown')
        elif action == "prev":
            # Shift + P is the official YouTube shortcut to go to the PREVIOUS video in a playlist
            pyautogui.keyDown('shift')
            pyautogui.press('p')
            pyautogui.keyUp('shift')
        elif action == "next":
            # Shift + N is the official YouTube shortcut to go to the NEXT video in a playlist
            pyautogui.keyDown('shift')
            pyautogui.press('n')
            pyautogui.keyUp('shift')
        elif action == "screenshot":
            pyautogui.hotkey('win', 'shift', 's')
        else:
            pyautogui.press(action)
