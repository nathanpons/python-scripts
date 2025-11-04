import customtkinter as ctk
from dotenv import load_dotenv
import os
from gui.main_window import MainWindow

load_dotenv()
weather_api_key = os.getenv("WEATHER_API_KEY")

if __name__ == "__main__":
    root = ctk.CTk()
    app = MainWindow(root, weather_api_key=weather_api_key)
    root.mainloop()