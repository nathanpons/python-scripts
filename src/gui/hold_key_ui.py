import customtkinter as ctk
import logging
from scripts.hold_key_script import HoldKeyScript

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

MODIFIER_KEYS = {"ctrl", "alt", "shift", "control"}


class HoldKeyUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.script = None

        self.default_font = ctk.CTkFont(family="Helvetica", size=16)
        self.title_font = ctk.CTkFont(
            family=self.default_font.cget("family"),
            size=self.default_font.cget("size") + 4,
            weight="bold",
        )

        self.hold_mouse_keys = ["left mouse", "right mouse"]
        self.toggle_keys = ["f6", "f7", "f8", "f9"]

        self.validate_keyboard_key_error_message = ""

        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI components for the Hold Key script."""
        # Title
        self.title_label = ctk.CTkLabel(
            self.parent_frame,
            text="Hold Key Script",
            font=self.title_font,
        )
        self.title_label.pack(pady=10)

        # Configuration frame
        config_frame = ctk.CTkFrame(self.parent_frame)
        config_frame.pack(padx=5, pady=5)

        # Select whether to hold keyboard or mouse key
        self.key_type_var = ctk.StringVar(value="mouse")
        self.key_type_switch = ctk.CTkSwitch(
            config_frame,
            text=f"Hold Key Type: {self.key_type_var.get()}",
            variable=self.key_type_var,
            onvalue="keyboard",
            offvalue="mouse",
            font=self.default_font,
            command=self.toggle_key_type_ui,
        )
        self.key_type_switch.grid(row=0, columnspan=2, padx=5, pady=2)

        # Hold Key Label
        self.hold_key_label = ctk.CTkLabel(
            config_frame,
            text="Select Key to Hold:",
            font=self.default_font,
        )
        self.hold_key_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)

        # Hold Mouse Key selection
        self.hold_mouse_key_var = ctk.StringVar(value=self.hold_mouse_keys[0])
        self.hold_mouse_key_optionmenu = ctk.CTkOptionMenu(
            config_frame,
            variable=self.hold_mouse_key_var,
            values=self.hold_mouse_keys,
            font=self.default_font,
        )
        self.hold_mouse_key_optionmenu.grid(row=1, column=1, padx=5, pady=2)

        # Hold Keyboard Key selection
        self.hold_keyboard_key_var = ctk.StringVar(value="a")
        self.hold_keyboard_key_entry = ctk.CTkEntry(
            config_frame,
            textvariable=self.hold_keyboard_key_var,
            font=self.default_font,
        )

        # Toggle Key selection
        self.toggle_key_label = ctk.CTkLabel(
            config_frame,
            text="Select Toggle Key:",
            font=self.default_font,
        )
        self.toggle_key_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.toggle_key_var = ctk.StringVar(value=self.toggle_keys[2])
        self.toggle_key_optionmenu = ctk.CTkOptionMenu(
            config_frame,
            variable=self.toggle_key_var,
            values=self.toggle_keys,
            font=self.default_font,
        )
        self.toggle_key_optionmenu.grid(row=2, column=1, padx=5, pady=2)

        # Invalid input error label
        self.validate_keyboard_key_error_label = ctk.CTkLabel(
            config_frame,
            text="",
            font=self.default_font,
            text_color="red",
            wraplength=300,
        )

        # Spam Key Switch
        self.is_spam_key_var = ctk.BooleanVar(value=False)
        self.spam_key_switch = ctk.CTkSwitch(
            config_frame,
            text="Press Rapidly Instead of Hold",
            variable=self.is_spam_key_var,
            font=self.default_font,
            command=self.toggle_interval_ui,
        )
        self.spam_key_switch.grid(row=4, columnspan=2, pady=5)

        # Interval settings
        self.interval_frame = ctk.CTkFrame(config_frame)
        self.interval_frame_label = ctk.CTkLabel(
            self.interval_frame,
            text="Interval:",
            font=self.default_font,
        )
        self.interval_frame_label.grid(row=5, column=0, sticky="w", padx=5)

        self.interval_var_milliseconds = ctk.StringVar(value="10")
        self.interval_label = ctk.CTkLabel(
            self.interval_frame,
            text="Milliseconds:",
            font=self.default_font,
        )
        self.interval_label.grid(row=6, column=0, sticky="w", padx=5)
        self.interval_entry = ctk.CTkEntry(
            self.interval_frame,
            textvariable=self.interval_var_milliseconds,
            font=self.default_font,
        )
        self.interval_entry.grid(row=6, column=1, sticky="w", padx=5)

        # Interval error label
        self.interval_error_label = ctk.CTkLabel(
            config_frame,
            text="",
            font=self.default_font,
            text_color="red",
            wraplength=300,
        )
        self.interval_frame_visible = False

        # Control buttons
        button_frame = ctk.CTkFrame(self.parent_frame)
        button_frame.pack(pady=5)

        self.toggle_script_button_text = ctk.StringVar(value="Start")
        self.toggle_script_button = ctk.CTkButton(
            button_frame,
            textvariable=self.toggle_script_button_text,
            font=self.default_font,
            command=self.toggle_script,
        )
        self.toggle_script_button.pack(side="left")

        # Status label
        self.status_label = ctk.CTkLabel(
            self.parent_frame,
            text="Status: Stopped",
            font=self.default_font,
        )
        self.status_label.pack(pady=10)

    def toggle_script(self):
        """Toggles the Hold Key script."""
        if self.script is None or not self.script.is_running:
            try:
                # Detect hold key based on selected key type
                if self.key_type_var.get() == "mouse":
                    self.key_var_value = self.hold_mouse_key_var.get()
                else:
                    self.key_var_value = self.hold_keyboard_key_var.get()

                # Validate inputs
                if self.is_spam_key_var.get():
                    if not self.validate_interval():
                        raise ValueError("Interval value must be a positive integer.")

                if self.key_type_var.get() == "keyboard":
                    if not self.validate_keyboard_key():
                        raise ValueError("Invalid hold keyboard key specified.")

                # Reset error messages
                self.reset_error_labels()

                # Start the script
                hold_key = self.key_var_value
                toggle_key = self.toggle_key_var.get()
                is_spam_key = self.is_spam_key_var.get()
                interval_milliseconds = int(self.interval_var_milliseconds.get())
                interval = interval_milliseconds / 1000.0  # Convert to seconds
                self.script = HoldKeyScript(
                    hold_key=hold_key,
                    toggle_key=toggle_key,
                    is_spam_key=is_spam_key,
                    interval=interval,
                )
                logging.debug(
                    f"Starting Hold Key Script with hold_key='{hold_key}' and toggle_key='{toggle_key}' with is_spam_key={is_spam_key}"
                )
                self.script.start()
                self.status_label.configure(text="Status: Running")
                self.key_type_switch.configure(state="disabled")
                self.hold_mouse_key_optionmenu.configure(state="disabled")
                self.hold_keyboard_key_entry.configure(state="disabled")
                self.toggle_key_optionmenu.configure(state="disabled")
                self.spam_key_switch.configure(state="disabled")
                self.interval_entry.configure(state="disabled")
                self.toggle_script_button_text.set("Stop")
            except Exception as e:
                logging.error(f"Failed to start Hold Key Script: {e}")

        else:
            try:
                # Stop the script
                self.script.stop()

                self.status_label.configure(text="Status: Stopped")
                self.key_type_switch.configure(state="normal")
                self.hold_mouse_key_optionmenu.configure(state="normal")
                self.hold_keyboard_key_entry.configure(state="normal")
                self.toggle_key_optionmenu.configure(state="normal")
                self.spam_key_switch.configure(state="normal")
                self.interval_entry.configure(state="normal")
                self.toggle_script_button_text.set("Start")
                self.script = None

                logging.debug("Stopped Hold Key Script.")
            except Exception as e:
                logging.error(f"Failed to stop Hold Key Script: {e}")

    def reset_error_labels(self):
        """Resets all error labels in the UI."""
        self.validate_keyboard_key_error_label.configure(text="")
        self.validate_keyboard_key_error_label.grid_remove()
        self.interval_error_label.configure(text="")
        self.interval_error_label.grid_remove()

    def validate_keyboard_key(self):
        """Validates that the hold keyboard key is a single character."""
        key = self.hold_keyboard_key_var.get()
        self.validate_keyboard_key_error_message = ""
        valid_keyboard_keys = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/? "

        logging.debug(f"Validating hold keyboard key: '{key}'")

        if key in MODIFIER_KEYS:
            logging.debug(f"Key found in modifier keys: '{key}'")
            logging.debug(f"Validated hold keyboard key '{key}' successful")
            self.validate_keyboard_key_error_label.configure(text="")
            self.validate_keyboard_key_error_label.grid_remove()
            return True

        if len(key) != 1:
            logging.error("Hold keyboard key must be a single character.")
            self.validate_keyboard_key_error_message = (
                "Error: \nHold keyboard key must be a single character."
            )
            self.validate_keyboard_key_error_label.configure(
                text=self.validate_keyboard_key_error_message
            )
            self.validate_keyboard_key_error_label.grid(
                row=3, column=0, columnspan=2, padx=5, pady=2
            )
            return False

        if key not in valid_keyboard_keys:
            logging.error("Hold keyboard key must be a printable character.")
            self.validate_keyboard_key_error_message = (
                "Error: \nHold keyboard key must be a printable character."
            )
            self.validate_keyboard_key_error_label.configure(
                text=self.validate_keyboard_key_error_message
            )
            self.validate_keyboard_key_error_label.grid(
                row=3, column=0, columnspan=2, padx=5, pady=2
            )
            return False

        logging.debug(f"Validated hold keyboard key '{key}' successful")
        self.validate_keyboard_key_error_label.configure(text="")
        self.validate_keyboard_key_error_label.grid_remove()
        return True

    def validate_interval(self):
        """Validates that the interval input is a positive integer."""
        try:
            value = int(self.interval_var_milliseconds.get())
            logging.debug(f"Validating interval value: {value}")

            if value <= 0:
                raise ValueError("Interval must be a positive integer.")

            logging.debug(f"Validated interval: {value} milliseconds.")
            self.interval_error_label.configure(text="")
            self.interval_error_label.grid_remove()
            return True
        except (ValueError, TypeError):
            logging.error("Interval value must be a positive integer.")
            self.interval_error_label.configure(
                text="Error: \nInterval must be a positive integer."
            )
            self.interval_error_label.grid(
                row=7, column=0, columnspan=2, padx=5, pady=2
            )
            return False
        except Exception as e:
            logging.error(f"Unexpected error during interval validation: {e}")
            return False

    def toggle_interval_ui(self):
        """Toggles the visibility of the interval settings UI."""
        if self.spam_key_switch.get():
            if not self.interval_frame_visible:
                self.interval_frame.grid(row=5, columnspan=2, pady=5)
                self.interval_frame_visible = True
        else:
            if self.interval_frame_visible:
                self.interval_frame.grid_forget()
                self.interval_frame_visible = False

    def toggle_key_type_ui(self):
        """Toggles the UI elements based on the selected key type."""
        key_type = self.key_type_var.get()
        self.key_type_switch.configure(text=f"Hold Key Type: {key_type.capitalize()}")
        if key_type == "mouse":
            self.hold_keyboard_key_entry.grid_remove()
            self.hold_mouse_key_optionmenu.grid(row=1, column=1, padx=5, pady=2)
        else:
            self.hold_mouse_key_optionmenu.grid_remove()
            self.hold_keyboard_key_entry.grid(row=1, column=1, padx=5, pady=2)

    def toggle_hold(self):
        """Toggles the hold state of the script."""
        if self.script and self.script.is_running:
            self.script.toggle_hold()
            logging.debug(f"Toggled hold state: {self.script.toggle}")

    def cleanup(self):
        """Cleans up the script on UI destruction."""
        if self.script and self.script.is_running:
            self.script.stop()

        if self.script:
            self.script = None
