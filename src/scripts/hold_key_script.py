import keyboard
import pyautogui
import threading
import time
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

MOUSE_KEYS = {
    "left mouse": "left",
    "right mouse": "right",
    "middle mouse": "middle"
}

class HoldKeyScript:
    def __init__(self, hold_key="w", toggle_key="f6", is_spam_key=False):
        self.thread = None
        self.hotkey_handler = None
        self.toggle = False
        self.running = False
        self.previous_toggle = False
        self.is_spam_key = is_spam_key
        self.hold_key = hold_key
        self.toggle_key = toggle_key
        self.is_mouse_key = self.hold_key in MOUSE_KEYS

    def hold_key_loop(self):
        """Main loop that holds or spams a key"""
        try:
            while self.running:
                if not self.is_mouse_key:
                    # Regular keyboard key handling
                    # Check for toggle state change
                    if self.toggle and not self.previous_toggle:
                        if self.is_spam_key:
                            logging.debug(f"Spamming '{self.hold_key}'.")
                        else:
                            logging.debug(f"Holding '{self.hold_key}'.")
                            keyboard.press(self.hold_key)

                    # If toggle turned off
                    elif not self.toggle and self.previous_toggle:
                        keyboard.release(self.hold_key)
                        logging.debug(f"Released '{self.hold_key}' key.")

                    if self.toggle and self.is_spam_key:
                        keyboard.press_and_release(self.hold_key)
                        logging.debug(f"Spamming '{self.hold_key}'.")

                else:
                    # Mouse handling
                    mouse_button = MOUSE_KEYS.get(self.hold_key)
                    if self.toggle and not self.previous_toggle:
                        if self.is_spam_key:
                            logging.debug(f"Spamming '{self.hold_key}' mouse button.")
                        else:
                            logging.debug(f"Holding '{self.hold_key}' mouse button.")
                            pyautogui.mouseDown(button=mouse_button)
                    elif not self.toggle and self.previous_toggle:
                        pyautogui.mouseUp(button=mouse_button)
                        logging.debug(f"Released '{self.hold_key}' mouse button.")
                    
                    if self.toggle and self.is_spam_key:
                        pyautogui.click(button=mouse_button)
                        logging.debug(f"Spamming '{self.hold_key}' mouse button.")

                self.previous_toggle = self.toggle
                time.sleep(0.01)

        except Exception as e:
            logging.error(f"Error in hold_key_loop: {e}")
        finally:
            logging.debug("Exiting hold_key_loop.")

    def start(self):
        """Starts the hold hold_key script."""
        if not self.running:
            self.running = True
            self.hotkey_handler = keyboard.add_hotkey(self.toggle_key, self.toggle_hold)
            self.thread = threading.Thread(target=self.hold_key_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stops the hold hold_key script."""
        if self.running:
            self.running = False
            self.toggle = False
            if self.is_mouse_key:
                mouse_button = MOUSE_KEYS.get(self.hold_key)
                pyautogui.mouseUp(button=mouse_button)
            else:
                keyboard.release(self.hold_key)
            if self.hotkey_handler:
                keyboard.remove_hotkey(self.hotkey_handler)
                self.hotkey_handler = None
                logging.debug(f"Unbound Toggle Key '{self.toggle_key}'.")
            if self.thread:
                self.thread.join(timeout=2)

    def toggle_hold(self):
        """Toggles the hold state."""
        self.toggle = not self.toggle
