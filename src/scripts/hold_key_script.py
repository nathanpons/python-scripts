import keyboard
import threading
import time

class HoldKeyScript:
    def __init__(self, hold_key='w', toggle_key='f6'):
        self.toggle = False
        self.thread = None
        self.running = False
        self.hold_key = hold_key
        self.toggle_key = toggle_key

    def hold_key_loop(self):
        """Main loop that holds a hold_key"""
        while self.running:
            if self.toggle:
                keyboard.press(self.hold_key)
                time.sleep(0.1)
            else:
                keyboard.release(self.hold_key)
                time.sleep(0.1)

    def start(self):
        """Starts the hold hold_key script."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.hold_key_loop)
            self.thread.start()

    def stop(self):
        """Stops the hold hold_key script."""
        if self.running:
            self.running = False
            self.toggle = False
            if self.thread:
                self.thread.join()
            keyboard.release(self.hold_key)

    def toggle_hold(self):
        """Toggles the hold state."""
        self.toggle = not self.toggle
        if self.toggle:
            print(f"Holding '{self.hold_key}' key.")
        else:
            print(f"Released '{self.hold_key}' key.")