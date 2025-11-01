import customtkinter as ctk
from .gui.main_window import MainWindow

if __name__ == "__main__":
    root = ctk.CTk()
    app = MainWindow(root)
    root.mainloop()