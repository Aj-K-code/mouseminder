import json
import time
import threading
from pynput import mouse, keyboard
import tkinter as tk
from tkinter import messagebox
import os
import sys

class MouseMinder:
    def __init__(self, config_path='config.json'):
        self.config = self.load_config(config_path)
        self.fidget_score = 0
        self.last_movement_time = time.time()
        self.last_mouse_position = (0, 0)
        self.is_locked = False
        self.lock_start_time = 0
        self.timeout_duration = 0
        self.offense_count = 0

        # Initialize listeners
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)

    def load_config(self, config_path):
        default_config = {
            "sensitivity": "medium",
            "timeouts": {
                "short": 5,
                "long": 15
            },
            "messages": [
                "Chill out!",
                "Focus, padawan!",
                "Stop the wiggle!",
                "Productivity police: You're under arrest!"
            ],
            "enable_sound": False,
            "whitelist": []
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    default_config.update(user_config)
                    for key in default_config:
                        if isinstance(default_config[key], dict) and key in user_config:
                            default_config[key].update(user_config[key])
                    return default_config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
        return default_config

    def get_sensitivity_threshold(self):
        # Define thresholds for different sensitivity levels
        # Lower threshold means more sensitive
        sensitivity_map = {
            "low": 2.0,
            "medium": 1.0,
            "high": 0.5
        }
        return sensitivity_map.get(self.config["sensitivity"], 1.0)

    def on_move(self, x, y):
        if self.is_locked:
            return

        current_time = time.time()
        dx = x - self.last_mouse_position[0]
        dy = y - self.last_mouse_position[1]
        distance = (dx**2 + dy**2)**0.5

        # Check if movement is significant
        if distance > 1: # Minimum pixel movement to consider
            time_diff = current_time - self.last_movement_time
            # If moved recently, it might be fidgeting
            if time_diff < 0.5: # Time window to consider fidgeting
                self.fidget_score += 1 * self.get_sensitivity_threshold()
            else:
                # Reset score if there was a pause
                self.fidget_score = max(0, self.fidget_score - 0.5)

            self.last_movement_time = current_time
            self.last_mouse_position = (x, y)

            # Check if fidget score is high enough to trigger action
            if self.fidget_score > 10:
                self.trigger_timeout()

    def on_click(self, x, y, button, pressed):
        if pressed:
            # Reset fidget score on click
            self.fidget_score = 0
            self.last_movement_time = time.time()
            self.last_mouse_position = (x, y)

    def on_key_press(self, key):
        # Reset fidget score on key press
        self.fidget_score = 0
        self.last_movement_time = time.time()

    def trigger_timeout(self):
        if self.is_locked:
            return

        self.offense_count += 1
        self.fidget_score = 0 # Reset score

        # Determine timeout duration based on offense count
        if self.offense_count == 1:
            # Warning only
            self.show_warning()
            return
        elif self.offense_count == 2:
            self.timeout_duration = self.config["timeouts"]["short"]
        else: # 3rd and subsequent offenses
            self.timeout_duration = self.config["timeouts"]["long"]

        self.is_locked = True
        self.lock_start_time = time.time()
        self.lock_mouse()
        self.show_message()

        # Start a thread to handle the timeout
        timeout_thread = threading.Thread(target=self.handle_timeout)
        timeout_thread.daemon = True
        timeout_thread.start()

    def show_warning(self):
        # Simple warning message
        root = tk.Tk()
        root.withdraw() # Hide the main window
        messagebox.showwarning("MouseMinder", "Fidgeting detected! Please be still.")
        root.destroy()

    def lock_mouse(self):
        # This is a placeholder. Actual implementation depends on OS.
        # For now, we'll just print a message.
        print("MOUSE LOCKED! Move to center and hold for timeout.")

    def unlock_mouse(self):
        # This is a placeholder. Actual implementation depends on OS.
        print("MOUSE UNLOCKED!")

    def show_message(self):
        # Simple message box for now
        message = f"Timeout! {self.timeout_duration} seconds. Offense #{self.offense_count}"
        if self.config["messages"]:
            import random
            message += f"\n{random.choice(self.config['messages'])}"

        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("MouseMinder", message)
        root.destroy()

    def handle_timeout(self):
        while self.is_locked and (time.time() - self.lock_start_time) < self.timeout_duration:
            time.sleep(0.1) # Check every 100ms

        if self.is_locked:
            self.is_locked = False
            self.unlock_mouse()

    def start(self):
        print("MouseMinder started. Monitoring mouse movements...")
        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping MouseMinder...")
            self.mouse_listener.stop()
            self.keyboard_listener.stop()

if __name__ == "__main__":
    app = MouseMinder()
    app.start()