import customtkinter as ctk
import sys
import os
from gui.hold_key_ui import HoldKeyUI


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Nathan's Python Scripts")
        self.root.geometry("400x450")

        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "assets", "favicon.ico")
        else:
            icon_path = "src/assets/favicon.ico"
        self.root.iconbitmap(icon_path)

        self.current_ui = None
        print("Initializing Main Window GUI...")
        self.setup_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(pady=10, padx=10, fill="x")

        # Header frame
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        header_label = ctk.CTkLabel(
            header_frame, text="Nathan's Python Scripts", font=("Helvetica", 16)
        )
        header_label.pack()

        # Script selector
        selection_frame = ctk.CTkFrame(main_frame)
        selection_frame.pack(fill="x", pady=(0, 20))

        selection_label = ctk.CTkLabel(selection_frame, text="Select a script")
        selection_label.pack(pady=10)

        self.scripts_list = ("None", "Hold_Key")
        self.script_type = ctk.StringVar()
        self.combobox = ctk.CTkComboBox(
            selection_frame, variable=self.script_type, values=self.scripts_list, command=self.on_selection
        )
        self.combobox.set("None")
        self.combobox.pack(pady=10)

        # Dynamic content
        self.dynamic_content_frame = ctk.CTkFrame(main_frame)
        self.dynamic_content_frame.pack(fill="both", expand=True)

        self.setup_default_ui()

    def on_selection(self, event):
        """Called when a new script is selected."""
        selection = self.script_type.get()
        print(f"Script selected: {selection}")

        self.clear_dynamic_content()

        match selection:
            case "Hold_Key":
                self.setup_hold_key_ui()
            case _:
                self.setup_default_ui()

    def clear_dynamic_content(self):
        """Clears the dynamic content frame."""
        if self.current_ui and hasattr(self.current_ui, "cleanup"):
            self.current_ui.cleanup()

        for widget in self.dynamic_content_frame.winfo_children():
            widget.destroy()

    def setup_hold_key_ui(self):
        """Sets up the UI for the Hold Key script."""
        self.current_ui = HoldKeyUI(self.dynamic_content_frame)

    def setup_default_ui(self):
        """Sets up the default UI when no script is selected."""
        self.default_ui_label = ctk.CTkLabel(
            self.dynamic_content_frame,
            text="Please select a script from the dropdown above.",
        )
        self.default_ui_label.pack(pady=20)

    def on_close(self):
        """Handles cleanup on window close."""
        if self.current_ui and hasattr(self.current_ui, "cleanup"):
            print("Closing application and cleaning up resources...")
            self.current_ui.cleanup()
            print("Cleanup complete.")
        self.root.destroy()
