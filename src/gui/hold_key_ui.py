import customtkinter as ctk
import logging
from scripts.hold_key_script import HoldKeyScript

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


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

        self.hold_keys = ["left mouse", "right mouse", "w", "a", "s", "d"]
        self.toggle_keys = ["f6", "f7", "f8", "f9"]

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
        config_frame.pack(pady=5)

        # Hold Key selection
        self.hold_key_label = ctk.CTkLabel(
            config_frame,
            text="Select Key to Hold:",
            font=self.default_font,
        )
        self.hold_key_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.hold_key_var = ctk.StringVar(value=self.hold_keys[0])
        self.hold_key_optionmenu = ctk.CTkOptionMenu(
            config_frame,
            variable=self.hold_key_var,
            values=self.hold_keys,
            font=self.default_font,
        )
        self.hold_key_optionmenu.grid(row=0, column=1, padx=5, pady=2)

        # Toggle Key selection
        self.toggle_key_label = ctk.CTkLabel(
            config_frame,
            text="Select Toggle Key:",
            font=self.default_font,
        )
        self.toggle_key_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.toggle_key_var = ctk.StringVar(value=self.toggle_keys[0])
        self.toggle_key_optionmenu = ctk.CTkOptionMenu(
            config_frame,
            variable=self.toggle_key_var,
            values=self.toggle_keys,
            font=self.default_font,
        )
        self.toggle_key_optionmenu.grid(row=1, column=1, padx=5, pady=2)

        # Spam Key Switch
        self.is_spam_key_var = ctk.BooleanVar(value=False)
        self.spam_key_switch = ctk.CTkSwitch(
            config_frame,
            text="Spam Key Instead of Hold",
            variable=self.is_spam_key_var,
            font=self.default_font,
            command=self.toggle_interval_ui,
        )
        self.spam_key_switch.grid(row=2, columnspan=2, pady=5)

        # Interval settings
        self.interval_frame = ctk.CTkFrame(config_frame)
        self.interval_frame_label = ctk.CTkLabel(
            self.interval_frame,
            text="Interval:",
            font=self.default_font,
        )
        self.interval_frame_label.grid(row=3, column=0, sticky="w", padx=5)

        self.interval_var_milliseconds = ctk.StringVar(value="10")
        self.interval_label = ctk.CTkLabel(
            self.interval_frame,
            text="Milliseconds:",
            font=self.default_font,
        )
        self.interval_label.grid(row=4, column=0, sticky="w", padx=5)
        self.interval_entry = ctk.CTkEntry(
            self.interval_frame,
            textvariable=self.interval_var_milliseconds,
            font=self.default_font,
        )
        self.interval_entry.grid(row=4, column=1, sticky="w", padx=5)

        # Interval error label
        self.interval_error_label = ctk.CTkLabel(
            config_frame,
            text="",
            font=self.default_font,
            text_color="red",
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
                if not self.validate_interval():
                    raise ValueError("Interval value must be a positive integer.")

                # Start the script
                hold_key = self.hold_key_var.get()
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
                self.hold_key_optionmenu.configure(state="disabled")
                self.toggle_key_optionmenu.configure(state="disabled")
                self.spam_key_switch.configure(state="disabled")
                self.toggle_script_button_text.set("Stop")
            except Exception as e:
                logging.error(f"Failed to start Hold Key Script: {e}")

        else:
            try:
                # Stop the script
                self.script.stop()

                self.hold_key_optionmenu.configure(state="normal")
                self.toggle_key_optionmenu.configure(state="normal")
                self.spam_key_switch.configure(state="normal")
                self.script = None
                logging.debug("Stopped Hold Key Script.")

                self.status_label.configure(text="Status: Stopped")
                self.toggle_script_button_text.set("Start")
            except Exception as e:
                logging.error(f"Failed to stop Hold Key Script: {e}")

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
                text="Error: Interval must be a positive integer."
            )
            self.interval_error_label.grid(
                row=5, column=0, columnspan=2, sticky="w", padx=5, pady=2
            )
            return False
        except Exception as e:
            logging.error(f"Unexpected error during interval validation: {e}")
            return False

    def toggle_interval_ui(self):
        """Toggles the visibility of the interval settings UI."""
        if self.spam_key_switch.get():
            if not self.interval_frame_visible:
                self.interval_frame.grid(row=3, columnspan=2, pady=5)
                self.interval_frame_visible = True
        else:
            if self.interval_frame_visible:
                self.interval_frame.grid_forget()
                self.interval_frame_visible = False

    def toggle_hold(self):
        """Toggles the hold state of the script."""
        if self.script and self.script.is_running:
            self.script.toggle_hold()
            logging.debug(f"Toggled hold state: {self.script.toggle}")

    def cleanup(self):
        """Cleans up the script on UI destruction."""
        if self.script and self.script.is_running:
            self.script.stop()
            self.script = None
