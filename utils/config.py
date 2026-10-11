import yaml
import os

class ConfigManager:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.settings = self.load_config()

    def load_config(self):
        """
        Loads the YAML configuration file.
        """
        if not os.path.exists(self.config_path):
            print(f"Warning: {self.config_path} not found. Using defaults.")
            return {
                "pinch_threshold": 0.04,
                "swipe_threshold": 0.07,
                "smoothing_window": 5,
                "stabilization_frames": 3,
                "actions": {
                    "FIST": "space",
                    "OPEN_PALM": "space",
                    "PINCH": "volumedown",
                    "SWIPE_LEFT": "prev",
                    "SWIPE_RIGHT": "next"
                }
            }
        
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return {}

    def get(self, key, default=None):
        return self.settings.get(key, default)
