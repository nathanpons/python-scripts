import keyboard
import pyautogui
import threading
import time
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

MOUSE_KEYS = {"left mouse": "left", "right mouse": "right", "middle mouse": "middle"}
MODIFIER_KEYS = {"ctrl", "alt", "shift", "control"}


class HoldKeyScript:
    def __init__(
        self,
        hold_key="w",
        toggle_key="f6",
        is_spam_key=False,
        interval=0.01,
        press_interval=0.01,
    ):
        self.thread = None
        self.hotkey_handler = None
        self.toggle = False
        self.is_running = False
        self.previous_toggle = False
        self.interval = interval
        self.press_interval = press_interval
        self.is_spam_key = is_spam_key
        self.hold_key = hold_key
        self.toggle_key = toggle_key
        self.is_mouse_key = self.hold_key in MOUSE_KEYS
        self.is_modifier_key = self.hold_key in MODIFIER_KEYS

    def hold_key_loop(self):
        """Main loop that holds or spams a key"""
        try:
            while self.is_running:
                if not self.is_mouse_key:
                    # Regular keyboard key handling
                    # Check for toggle state change
                    if self.toggle and not self.previous_toggle:
                        if self.is_spam_key:
                            logging.debug(f"Pressing '{self.hold_key}'.")
                        else:
                            logging.debug(f"Holding '{self.hold_key}'.")
                            keyboard.press(self.hold_key)

                    # If toggle turned off
                    elif not self.toggle and self.previous_toggle:
                        keyboard.release(self.hold_key)
                        logging.debug(f"Released '{self.hold_key}' key.")

                    if self.toggle and self.is_spam_key:
                        keyboard.press(self.hold_key)
                        time.sleep(
                            self.press_interval
                        )  # Short delay to simulate key press
                        keyboard.release(self.hold_key)
                        logging.debug(f"Pressing '{self.hold_key}'.")

                else:
                    # Mouse handling
                    mouse_button = MOUSE_KEYS.get(self.hold_key)
                    if self.toggle and not self.previous_toggle:
                        if self.is_spam_key:
                            logging.debug(f"Clicking '{self.hold_key}' mouse button.")
                        else:
                            logging.debug(f"Holding '{self.hold_key}' mouse button.")
                            pyautogui.mouseDown(button=mouse_button)
                    elif not self.toggle and self.previous_toggle:
                        pyautogui.mouseUp(button=mouse_button)
                        logging.debug(f"Released '{self.hold_key}' mouse button.")

                    if self.toggle and self.is_spam_key:
                        pyautogui.click(button=mouse_button)
                        logging.debug(f"Clicking '{self.hold_key}' mouse button.")

                self.previous_toggle = self.toggle
                time.sleep(self.interval)

        except Exception as e:
            logging.error(f"Error in hold_key_loop: {e}")
        finally:
            logging.debug("Exiting hold_key_loop.")

    def start(self):
        """Starts the hold hold_key script."""
        try:
            if self.interval <= 0:
                raise ValueError("Interval must be a positive number.")
            if not self.is_running:
                self.is_running = True
                self.hotkey_handler = keyboard.add_hotkey(
                    self.toggle_key, self.toggle_hold
                )
                self.thread = threading.Thread(target=self.hold_key_loop, daemon=True)
                self.thread.start()
        except ValueError as e:
            logging.error(f"Invalid key specified: {e}")
            raise
        except Exception as e:
            logging.error(f"Error starting hold_key_script: {e}")
            raise

    def stop(self):
        """Stops the hold hold_key script."""
        if self.is_running:
            self.is_running = False
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
