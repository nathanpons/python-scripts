import tkinter as tk
import ttkbootstrap as ttk
from .gui.main_window import MainWindow

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = MainWindow(root)
    root.mainloop()