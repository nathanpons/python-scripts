import tkinter as tk
import ttkbootstrap as ttk
import logging
from ..scripts.hold_key_script import HoldKeyScript

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class HoldKeyUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.script = None

        self.hold_keys = ["left mouse", "right mouse", "w", "a", "s", "d"]
        self.toggle_keys = ["f6", "f7", "f8", "f9"]

        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI components for the Hold Key script."""
        # Title
        self.title_label = ttk.Label(self.parent_frame, text="Hold Key Script")
        self.title_label.pack(pady=10)

        # Configuration frame
        config_frame = ttk.Frame(self.parent_frame)
        config_frame.pack(pady=5)

        # Hold Key selection
        self.hold_key_label = ttk.Label(config_frame, text="Select Key to Hold:")
        self.hold_key_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.hold_key_var = tk.StringVar(value=self.hold_keys[0])
        self.hold_key_combobox = ttk.Combobox(
            config_frame,
            textvariable=self.hold_key_var,
            values=self.hold_keys,
            state="readonly",
        )
        self.hold_key_combobox.grid(row=0, column=1, padx=5, pady=2)

        # Toggle Key selection
        self.toggle_key_label = ttk.Label(config_frame, text="Select Toggle Key:")
        self.toggle_key_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.toggle_key_var = tk.StringVar(value=self.toggle_keys[0])
        self.toggle_key_combobox = ttk.Combobox(
            config_frame,
            textvariable=self.toggle_key_var,
            values=self.toggle_keys,
            state="readonly",
        )
        self.toggle_key_combobox.grid(row=1, column=1, padx=5, pady=2)

        # Spam Key Checkbox
        self.is_spam_key_var = tk.BooleanVar(value=False)
        self.spam_key_checkbox = ttk.Checkbutton(
            config_frame, text="Spam Key Instead of Hold", variable=self.is_spam_key_var
        )
        self.spam_key_checkbox.grid(row=2, columnspan=2, pady=5)

        # Control buttons
        button_frame = ttk.Frame(self.parent_frame)
        button_frame.pack(pady=5)

        self.toggle_script_button_text = tk.StringVar(value="Start")
        self.toggle_script_button = ttk.Button(
            button_frame,
            textvariable=self.toggle_script_button_text,
            command=self.toggle_script,
        )
        self.toggle_script_button.pack(side="left", padx=5)

        # Status label
        self.status_label = ttk.Label(self.parent_frame, text="Status: Stopped")
        self.status_label.pack(pady=10)

    def toggle_script(self):
        """Toggles the Hold Key script."""
        if self.script is None or not self.script.running:
            # Start the script
            hold_key = self.hold_key_var.get()
            toggle_key = self.toggle_key_var.get()
            is_spam_key = self.is_spam_key_var.get()
            self.script = HoldKeyScript(
                hold_key=hold_key, toggle_key=toggle_key, is_spam_key=is_spam_key
            )
            logging.debug(
                f"Starting Hold Key Script with hold_key='{hold_key}' and toggle_key='{toggle_key}' with is_spam_key={is_spam_key}"
            )
            self.script.start()

            self.status_label.config(text="Status: Running")
            self.hold_key_combobox.config(state="disabled")
            self.toggle_key_combobox.config(state="disabled")
            self.toggle_script_button_text.set("Stop")
        else:
            # Stop the script
            self.script.stop()
            self.script = None
            logging.debug("Stopped Hold Key Script.")

            self.status_label.config(text="Status: Stopped")
            self.hold_key_combobox.config(state="readonly")
            self.toggle_key_combobox.config(state="readonly")
            self.toggle_script_button_text.set("Start")

    def toggle_hold(self):
        """Toggles the hold state of the script."""
        if self.script and self.script.running:
            self.script.toggle_hold()
            logging.debug(f"Toggled hold state: {self.script.toggle}")

    def cleanup(self):
        """Cleans up the script on UI destruction."""
        if self.script and self.script.running:
            self.script.stop()
