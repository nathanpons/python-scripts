"""
Key logger for end-to-end tests.
"""
import customtkinter as ctk
from datetime import datetime

class KeyLoggerWindow:
    """A simple key logger window using CustomTkinter."""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Key Logger")
        self.root.geometry("400x300")
        
        self.text_area = ctk.CTkTextbox(self.root, width=380, height=280)
        self.text_area.pack(pady=10, padx=10)

        self.text_area.insert(ctk.END, "Key Logger Started...\n")
        self.text_area.configure(state=ctk.DISABLED)
        
        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("<Button>", self.on_mouse_click)
        self.root.bind("<Button-2>", self.on_mouse_click)
        self.root.bind("<Button-3>", self.on_mouse_click)

        self.key_log = []

    def on_key_press(self, event):
        """Logs the pressed key with a timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")[:-3]
        log_entry = f"[{timestamp}] Key: {event.char or event.keysym}\n"
        
        # Enable editing temporarily
        self.text_area.configure(state=ctk.NORMAL)
        self.text_area.insert(ctk.END, log_entry)
        self.text_area.see(ctk.END)

        # Disable editing again
        self.text_area.configure(state=ctk.DISABLED)

        self.key_log.append({
            "timestamp": timestamp,
            "type": "key",
            "key": event.char or event.keysym
        })

    def on_mouse_click(self, event):
        """Logs the mouse click with a timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")[:-3]
        button_map = {1: "Left", 2: "Middle", 3: "Right"}
        button = button_map.get(event.num, "Unknown")
        log_entry = f"[{timestamp}] - Mouse: {button} click at ({event.x}, {event.y})\n"

        # Enable editing temporarily
        self.text_area.configure(state=ctk.NORMAL)
        self.text_area.insert(ctk.END, log_entry)
        self.text_area.see(ctk.END)

        # Disable editing again
        self.text_area.configure(state=ctk.DISABLED)

        self.key_log.append({
            "timestamp": timestamp,
            "type": "mouse",
            "button": button
        })

    def get_text_content(self):
        """Returns the content of the text area."""
        return self.text_area.get("1.0", ctk.END)
    
    def clear(self):
        """Clears the text area."""
        self.text_area.delete("1.0", ctk.END)
        self.key_log = []

    def run(self):
        """Runs the key logger window."""
        self.root.mainloop()

if __name__ == "__main__":
    key_logger = KeyLoggerWindow()
    key_logger.run()