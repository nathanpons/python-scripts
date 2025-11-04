import customtkinter as ctk
from scripts.weather_script import WeatherScript

class WeatherUI:
    def __init__(self, parent, api_key):
        self.parent = parent
        self.api_key = api_key
        self.weather_script = WeatherScript(api_key)

        self.setup_ui()

    def setup_ui(self):
        self.city_label = ctk.CTkLabel(self.parent, text="Enter Country or City Name:")
        self.city_label.pack(pady=5)
        self.city_entry = ctk.CTkEntry(self.parent)
        self.city_entry.pack(pady=5)
        self.get_weather_button = ctk.CTkButton(
            self.parent, text="Get Weather", command=lambda: self.display_weather(
                self.weather_script.get_weather(self.city_entry.get())
            )
        )
        self.get_weather_button.pack(pady=5)
        self.result_label = ctk.CTkLabel(self.parent, text="")
        self.result_label.pack(pady=5)

    def display_weather(self, weather_data):
        if "error" in weather_data:
            self.result_label.configure(
                text=f"Error fetching data: {weather_data['error']}"
            )
        else:
            weather_info = (
                f"Weather: {weather_data['weather']}\n"
                f"Temperature: {weather_data['temperature']:.1f} °C | {weather_data['temperature'] * 9/5 + 32:.1f} °F\n"
                f"Humidity: {weather_data['humidity']}%\n"
                f"Description: {weather_data['description']}"
            )
            self.result_label.configure(text=weather_info)