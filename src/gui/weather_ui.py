import logging
import customtkinter as ctk
from PIL import Image
from scripts.weather_script import WeatherScript

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class WeatherUI:
    def __init__(self, parent):
        self.parent = parent
        self.weather_script = WeatherScript()

        self.default_font = ctk.CTkFont(family="Helvetica", size=16)
        self.title_font = ctk.CTkFont(
            family=self.default_font.cget("family"),
            size=self.default_font.cget("size") + 4,
            weight="bold",
        )

        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI components for the Weather script."""
        # Main Dashboard Frame
        self.dashboard_frame = ctk.CTkFrame(
            self.parent, corner_radius=10, border_width=2
        )
        self.dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=4)
        self.dashboard_frame.grid_rowconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(1, weight=4)

        # Title label
        self.title_label = ctk.CTkLabel(
            self.dashboard_frame, text="Weather Dashboard", font=self.title_font
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Location Input
        self.location_frame = ctk.CTkFrame(self.dashboard_frame)
        self.location_frame.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)

        self.location_label = ctk.CTkLabel(
            self.location_frame, text="Enter Location:", font=self.default_font
        )
        self.location_label.pack(padx=10, pady=5)

        self.location_entry_var = ctk.StringVar()
        self.location_entry = ctk.CTkEntry(
            self.location_frame,
            textvariable=self.location_entry_var,
            width=200,
            font=self.default_font,
        )
        self.location_entry.pack(padx=10, pady=5)

        self.get_weather_button = ctk.CTkButton(
            self.location_frame,
            text="Get Weather",
            font=self.default_font,
            command=lambda: self.display_weather(
                self.weather_script.get_weather(self.location_entry.get())
            ),
        )
        self.get_weather_button.pack(padx=10, pady=5)

        # Weather Display
        self.weather_frame = ctk.CTkFrame(self.dashboard_frame, corner_radius=10)
        self.weather_frame.grid(column=1, row=1, sticky="nsew", padx=10, pady=10)

        self.weather_frame.grid_rowconfigure(0, weight=1)  # Title row
        self.weather_frame.grid_rowconfigure(1, weight=1)  # Icon row
        self.weather_frame.grid_rowconfigure(2, weight=1)  # Info row
        self.weather_frame.grid_columnconfigure(0, weight=1)

        self.weather_title_label = ctk.CTkLabel(
            self.weather_frame, text="Current Weather", font=self.title_font
        )
        self.weather_title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.weather_icon = ctk.CTkLabel(
            self.weather_frame, text="", font=self.default_font
        )
        self.weather_icon.grid(row=1, column=0, padx=10, pady=10)

        self.weather_info_label = ctk.CTkLabel(
            self.weather_frame, text="Weather Information", font=self.default_font
        )
        self.weather_info_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def fetch_and_display_weather(self):
        location = self.location_entry_var.get()
        if not location or not location.strip():
            self.weather_info_label.configure(text="Please enter a valid location.")
            return
        try:
            weather_data = self.weather_script.get_weather(location.strip())
        except Exception as e:
            weather_data = "error"
            logging.error(f"Error fetching weather data: {e}")
        self.display_weather(weather_data)

    def display_weather(self, weather_data):
        if "error" in weather_data:
            self.weather_info_label.configure(
                text="Error fetching data, please try again later."
            )
        else:
            weather_info = (
                f"Weather: {weather_data['weather']}\n"
                f"Temperature: {weather_data['temperature']:.1f} °C | {weather_data['temperature'] * 9/5 + 32:.1f} °F\n"
                f"Humidity: {weather_data['humidity']}%\n"
                f"Description: {weather_data['description']}"
            )
            self.weather_info_label.configure(text=weather_info)

        # Update weather icon
        try:
            if weather_data.get("icon_path"):
                image = Image.open(weather_data["icon_path"])
                weather_icon_image = ctk.CTkImage(image, size=(100, 100))
                self.weather_icon.configure(image=weather_icon_image)
            else:
                self.weather_icon.configure(image=None)
        except FileNotFoundError as e:
            logging.error(f"Weather icon file not found: {e}")
            self.weather_icon.configure(image=None)
        except Exception as e:
            logging.error(f"Error loading weather icon: {e}")
            self.weather_icon.configure(image=None)
