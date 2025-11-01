import customtkinter as ctk
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
        self.title_label = ctk.CTkLabel(self.parent_frame, text="Hold Key Script")
        self.title_label.pack(pady=10)

        # Configuration frame
        config_frame = ctk.CTkFrame(self.parent_frame)
        config_frame.pack(pady=5)

        # Hold Key selection
        self.hold_key_label = ctk.CTkLabel(config_frame, text="Select Key to Hold:")
        self.hold_key_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.hold_key_var = ctk.StringVar(value=self.hold_keys[0])
        self.hold_key_combobox = ctk.CTkComboBox(
            config_frame,
            variable=self.hold_key_var,
            values=self.hold_keys,
        )
        self.hold_key_combobox.grid(row=0, column=1, padx=5, pady=2)

        # Toggle Key selection
        self.toggle_key_label = ctk.CTkLabel(config_frame, text="Select Toggle Key:")
        self.toggle_key_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.toggle_key_var = ctk.StringVar(value=self.toggle_keys[0])
        self.toggle_key_combobox = ctk.CTkComboBox(
            config_frame,
            variable=self.toggle_key_var,
            values=self.toggle_keys,
        )
        self.toggle_key_combobox.grid(row=1, column=1, padx=5, pady=2)

        # Spam Key Switch
        self.is_spam_key_var = ctk.BooleanVar(value=False)
        self.spam_key_switch = ctk.CTkSwitch(
            config_frame, text="Spam Key Instead of Hold", variable=self.is_spam_key_var
        )
        self.spam_key_switch.grid(row=2, columnspan=2, pady=5)

        # Control buttons
        button_frame = ctk.CTkFrame(self.parent_frame)
        button_frame.pack(pady=5)

        self.toggle_script_button_text = ctk.StringVar(value="Start")
        self.toggle_script_button = ctk.CTkButton(
            button_frame,
            textvariable=self.toggle_script_button_text,
            command=self.toggle_script,
        )
        self.toggle_script_button.pack(side="left", padx=5)

        # Status label
        self.status_label = ctk.CTkLabel(self.parent_frame, text="Status: Stopped")
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

            self.status_label.configure(text="Status: Running")
            self.hold_key_combobox.configure(state="disabled")
            self.toggle_key_combobox.configure(state="disabled")
            self.spam_key_switch.configure(state="disabled")
            self.toggle_script_button_text.set("Stop")
        else:
            # Stop the script
            self.script.stop()
            
            self.hold_key_combobox.configure(state="normal")
            self.toggle_key_combobox.configure(state="normal")
            self.spam_key_switch.configure(state="normal")
            self.script = None
            logging.debug("Stopped Hold Key Script.")

            self.status_label.configure(text="Status: Stopped")
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
