import json
import time
import threading
from pynput import mouse, keyboard
import tkinter as tk
from tkinter import messagebox
import os
import sys
import random

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
        self.screen_width = 1920  # Default, will be updated
        self.screen_height = 1080 # Default, will be updated
        self.update_screen_dimensions()
        self.fidget_start_time = time.time()  # Track when fidgeting started
        
        # For dragging the mouse
        self.mouse_controller = mouse.Controller()
        
        # Initialize listeners
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        
        # For timeout handling
        self.timeout_thread = None

    def update_screen_dimensions(self):
        """Get the current screen dimensions of the primary monitor."""
        try:
            # For Linux, we can try to get dimensions using xrandr
            import subprocess
            output = subprocess.check_output(['xrandr']).decode('utf-8')
            
            # Look for the primary display
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if ' primary ' in line and ' connected' in line:
                    # This is the primary display
                    parts = line.split()
                    for part in parts:
                        if 'x' in part and '+' in part:
                            # Format like "1920x1080+0+0"
                            resolution_part = part.split('+')[0]
                            self.screen_width, self.screen_height = map(int, resolution_part.split('x'))
                            return
                            
            # Fallback: if no primary display found, use the first connected display with offset 0,0
            for i, line in enumerate(lines):
                if ' connected' in line:
                    # This is a connected display
                    parts = line.split()
                    for part in parts:
                        if 'x' in part and '+' in part:
                            # Format like "1920x1080+0+0"
                            offset_parts = part.split('+')
                            x_offset = int(offset_parts[1])
                            y_offset = int(offset_parts[2])
                            # If offset is 0,0 it's likely the primary
                            if x_offset == 0 and y_offset == 0:
                                resolution_part = offset_parts[0]
                                self.screen_width, self.screen_height = map(int, resolution_part.split('x'))
                                return
                                
            # Last fallback: use tkinter to get screen dimensions
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            self.screen_width = root.winfo_screenwidth()
            self.screen_height = root.winfo_screenheight()
            root.destroy()
        except Exception as e:
            print(f"Could not determine screen size, using defaults: {e}")

    def load_config(self, config_path):
        default_config = {
            "sensitivity": "high",  # Make it more sensitive
            "timeouts": {
                "short": 5,  # Changed to 5 seconds
                "long": 5   # Changed to 5 seconds
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
            # Continue dragging to center during lock
            self.drag_to_center()
            return

        current_time = time.time()
        dx = x - self.last_mouse_position[0]
        dy = y - self.last_mouse_position[1]
        distance = (dx**2 + dy**2)**0.5

        # Check if movement is significant
        if distance > 1: # Minimum pixel movement to consider
            # Update position
            self.last_mouse_position = (x, y)
            
            # Only increase fidget score if there's continuous movement
            time_diff = current_time - self.last_movement_time
            if time_diff < 0.5: # If moved recently, it might be fidgeting
                self.fidget_score += 1 * self.get_sensitivity_threshold()
                print(f"Fidgeting detected! Score: {self.fidget_score:.2f}")
            else:
                # Reset score if there was a pause
                if self.fidget_score > 0:
                    print(f"Pause detected, fidget score: {self.fidget_score:.2f} -> 0")
                self.fidget_score = 0
                self.fidget_start_time = current_time

        # Always update the last movement time
        self.last_movement_time = current_time

        # Check if fidgeting has been continuous for 5 seconds
        if self.fidget_score > 0 and (current_time - self.fidget_start_time) >= 5:
            print("5 seconds of continuous fidgeting detected!")
            self.trigger_timeout()

    def on_click(self, x, y, button, pressed):
        if pressed:
            # Reset fidget score on click
            self.fidget_score = 0
            self.last_movement_time = time.time()
            self.last_mouse_position = (x, y)
            
            # If clicked while locked, extend the lock
            if self.is_locked:
                self.lock_start_time = time.time()  # Reset the timer

    def on_key_press(self, key):
        # Reset fidget score on key press
        self.fidget_score = 0
        self.last_movement_time = time.time()
        self.fidget_start_time = time.time()  # Reset fidget start time

    def on_scroll(self, x, y, dx, dy):
        # Reset fidget score on scroll
        self.fidget_score = 0
        self.last_movement_time = time.time()
        self.fidget_start_time = time.time()  # Reset fidget start time

    def drag_to_center(self):
        """Move the mouse cursor towards the center of the primary screen."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Get current position
        current_x, current_y = self.mouse_controller.position
        
        # Calculate new position (move 5% of the distance to center each time)
        new_x = current_x + (center_x - current_x) * 0.05
        new_y = current_y + (center_y - current_y) * 0.05
        
        # Move the mouse
        self.mouse_controller.position = (new_x, new_y)

    # def show_simple_indicator(self):
    #     """Show a simple text indicator near the mouse cursor."""
    #     # For simplicity, we'll just print to console
    #     # In a full implementation, this would be a GUI element
    #     emojis = ["✋", "🤚", "🖐", "✋", "🤚", "Stop Fidgeting!"]
    #     print(f"\r{random.choice(emojis)}", end="", flush=True)

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
        print(f"\nMOUSE LOCKED! Dragging to center for {self.timeout_duration} seconds. Offense #{self.offense_count}")
        
        # Show the message immediately
        self.show_message()
        
        # Handle timeout in the main loop instead of a separate thread
        # We'll set a flag and let the main loop handle it
        print("[Lock initiated - waiting for timeout in main loop]")

    def show_warning(self):
        # Simple warning message
        root = tk.Tk()
        root.withdraw() # Hide the main window
        messagebox.showwarning("MouseMinder", "Fidgeting detected! Please be still.")
        root.destroy()

    def show_message(self):
        """Show message box in the center of the screen."""
        # Simple message box for now
        message = f"Timeout! {self.timeout_duration} seconds. Offense #{self.offense_count}"
        if self.config["messages"]:
            message += f"\n{random.choice(self.config['messages'])}"

        # Create a temporary root window for positioning
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Calculate center position
        x = self.screen_width // 2 - 200  # Approximate width/2
        y = self.screen_height // 2 - 75  # Approximate height/2
        
        # Show messagebox (positioning might not work on all systems)
        # We'll try to set the focus and position
        root.geometry(f"1x1+{x}+{y}")
        root.attributes('-topmost', True)
        
        messagebox.showinfo("MouseMinder", message)
        root.destroy()

    def handle_timeout(self):
        start_time = time.time()
        popup_shown = False
        
        # Show the message at the beginning of the timeout
        self.show_message()
        popup_shown = True
        
        # Lock duration
        lock_end_time = self.lock_start_time + self.timeout_duration
        
        print(f"Lock started at {self.lock_start_time}, will end at {lock_end_time}")
        print(f"Timeout duration: {self.timeout_duration} seconds")
        
        try:
            while self.is_locked and time.time() < lock_end_time:
                if self.is_locked:  # Check again in case it was unlocked
                    self.drag_to_center()
                    
                    # After 3 seconds, indicate popup would be hidden but continue locking
                    if (time.time() - start_time) >= 3 and popup_shown:
                        print("\n[Popup hidden - still in lockdown]")
                        popup_shown = False
                        
                time.sleep(0.05) # Check and update position every 50ms
                
                # Debug output
                remaining_time = lock_end_time - time.time()
                if remaining_time > 0:
                    print(f"Time remaining: {remaining_time:.2f} seconds", end="\r")
                elif remaining_time <= 0:
                    print(f"Time's up! Should unlock now.")
        except Exception as e:
            print(f"\nError in handle_timeout: {e}")
        finally:
            # Unlock the mouse
            if self.is_locked:
                self.is_locked = False
                print("\nMOUSE UNLOCKED!")
                # Reset fidget tracking when unlocked
                self.fidget_score = 0
                self.fidget_start_time = time.time()
            else:
                print("\nMouse was already unlocked")

    def start(self):
        print("MouseMinder started. Monitoring mouse movements...")
        print(f"Screen size: {self.screen_width}x{self.screen_height}")
        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            # Keep the main thread alive
            popup_shown = False
            start_time = 0
            
            while True:
                # Check if we're in a locked state
                if self.is_locked:
                    # Handle mouse dragging
                    self.drag_to_center()
                    
                    # Handle timeout
                    if time.time() - self.lock_start_time >= self.timeout_duration:
                        # Time's up, unlock the mouse
                        self.is_locked = False
                        print("\nMOUSE UNLOCKED!")
                        # Reset fidget tracking when unlocked
                        self.fidget_score = 0
                        self.fidget_start_time = time.time()
                        popup_shown = False
                    
                    # Handle popup visibility (show for first 3 seconds)
                    if not popup_shown:
                        # Popup was already shown in trigger_timeout, so we just track the state
                        popup_shown = True
                        start_time = time.time()
                    
                    if popup_shown and (time.time() - start_time) >= 3:
                        print("\n[Popup hidden - still in lockdown]")
                        popup_shown = False
                        
                    time.sleep(0.05)  # Check and update position every 50ms
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping MouseMinder...")
            self.mouse_listener.stop()
            self.keyboard_listener.stop()

if __name__ == "__main__":
    app = MouseMinder()
    app.start()