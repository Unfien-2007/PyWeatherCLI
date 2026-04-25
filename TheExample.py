# =============================================================================
#  PyWeatherCLI — Weather Application
#  Powered by OpenWeatherMap API
#  Modules: requests, json, datetime, matplotlib
# =============================================================================

import requests
import json
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ------------------------------------------------------------------------------
#  CONFIG  —  replace with your free key from openweathermap.org/api
# ------------------------------------------------------------------------------
API_KEY  = "762474eb41860948079ca87d6030807f"
BASE_URL = "https://api.openweathermap.org/data/2.5"
UNITS    = "metric"


# ==============================================================================
#  CLASSES
# ==============================================================================

class WeatherData:
    """Represents current weather conditions for a city."""

    def __init__(self, city, country, temp, feels_like, humidity, description, wind_speed):
        self.city        = city
        self.country     = country
        self.temp        = temp
        self.feels_like  = feels_like
        self.humidity    = humidity
        self.description = description
        self.wind_speed  = wind_speed

    def to_display(self):
        """Returns a formatted multi-line string of current weather."""
        return (
            f"\n{'='*44}\n"
            f"  {self.city}, {self.country}\n"
            f"{'='*44}\n"
            f"  Condition   : {self.description.title()}\n"
            f"  Temperature : {self.temp}°C  (feels like {self.feels_like}°C)\n"
            f"  Humidity    : {self.humidity}%\n"
            f"  Wind Speed  : {self.wind_speed} m/s\n"
            f"{'='*44}"
        )

    def summary(self):
        """Returns a compact one-line summary string."""
        return f"{self.city}: {self.temp}°C — {self.description.title()}"


class ForecastData(WeatherData):
    """
    Extends WeatherData to also hold a list of hourly forecast entries.
    Demonstrates inheritance: ForecastData IS-A WeatherData.
    """

    def __init__(self, city, country):
        # Call parent constructor with placeholder current-condition values;
        # these get filled in once we also fetch current weather.
        super().__init__(city, country, temp=None, feels_like=None,
                         humidity=None, description="", wind_speed=None)
        self.timestamps   = []   # list of datetime objects
        self.temperatures = []   # list of float temps
        self.descriptions = []   # list of condition strings

    def add_entry(self, timestamp, temp, description):
        """Appends one 3-hour forecast slot."""
        self.timestamps.append(timestamp)
        self.temperatures.append(temp)
        self.descriptions.append(description)

    def get_4day_slice(self):
        """Returns the first 32 entries (4 days × 8 slots of 3 hrs each)."""
        return self.timestamps[:32], self.temperatures[:32], self.descriptions[:32]


# ==============================================================================
#  USER-DEFINED FUNCTIONS
# ==============================================================================

def get_current_weather(city):
    """
    Fetches current weather for the given city via the OpenWeatherMap API.
    Returns a WeatherData object, or None on failure.
    """
    params = {"q": city, "appid": API_KEY, "units": UNITS}

    try:
        response = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return WeatherData(
                city        = data["name"],
                country     = data["sys"]["country"],
                temp        = round(data["main"]["temp"], 1),
                feels_like  = round(data["main"]["feels_like"], 1),
                humidity    = data["main"]["humidity"],
                description = data["weather"][0]["description"],
                wind_speed  = data["wind"]["speed"]
            )
        elif response.status_code == 404:
            print(f"\n  [!] City '{city}' not found. Check the spelling.")
        elif response.status_code == 401:
            print("\n  [!] Invalid API key — update API_KEY at the top of this file.")
        else:
            print(f"\n  [!] API error {response.status_code}.")

    except requests.exceptions.ConnectionError:
        print("\n  [!] No internet connection.")
    except requests.exceptions.Timeout:
        print("\n  [!] Request timed out — try again.")

    return None


def get_forecast(city):
    """
    Fetches 5-day / 3-hour forecast for the given city.
    Returns a ForecastData object, or None on failure.
    """
    params = {"q": city, "appid": API_KEY, "units": UNITS}

    try:
        response = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)

        if response.status_code == 200:
            data     = response.json()
            forecast = ForecastData(
                city    = data["city"]["name"],
                country = data["city"]["country"]
            )

            for entry in data["list"]:
                timestamp   = datetime.datetime.fromtimestamp(entry["dt"])
                temp        = round(entry["main"]["temp"], 1)
                description = entry["weather"][0]["description"]
                forecast.add_entry(timestamp, temp, description)

            return forecast

        elif response.status_code == 404:
            print(f"\n  [!] City '{city}' not found.")
        else:
            print(f"\n  [!] Could not fetch forecast: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("\n  [!] No internet connection.")
    except requests.exceptions.Timeout:
        print("\n  [!] Request timed out.")

    return None


def display_forecast_text(forecast):
    """
    Prints a day-by-day text forecast to the terminal,
    using nested loops and conditional logic.
    """
    timestamps, temperatures, descriptions = forecast.get_4day_slice()

    print(f"\n{'='*44}")
    print(f"  4-Day Forecast — {forecast.city}, {forecast.country}")
    print(f"{'='*44}")

    current_day = None

    for ts, temp, desc in zip(timestamps, temperatures, descriptions):
        day_label = ts.strftime("%A, %b %d")

        # Nested condition: print a day header when the date changes
        if day_label != current_day:
            if current_day is not None:
                print()          # blank line between days
            print(f"\n  {day_label}")
            print(f"  {'-'*34}")
            current_day = day_label

        time_str = ts.strftime("%I:%M %p")
        print(f"    {time_str}  →  {temp:>5.1f}°C  |  {desc.title()}")

    print(f"\n{'='*44}")


def plot_forecast(forecast):
    """
    Draws a Matplotlib line graph of the 4-day hourly temperature forecast.
    Meets the data visualization requirement.
    """
    timestamps, temperatures, _ = forecast.get_4day_slice()

    if not timestamps:
        print("  [!] No forecast data available to plot.")
        return

    fig, ax = plt.subplots(figsize=(13, 5))

    # ── Main line + markers ──────────────────────────────────────────────────
    ax.plot(
        timestamps, temperatures,
        color="#3B8BD4", linewidth=2,
        marker="o", markersize=4,
        markerfacecolor="white", markeredgewidth=1.5,
        label="Temperature (°C)"
    )

    # ── Shaded area under the line ───────────────────────────────────────────
    ax.fill_between(timestamps, temperatures, min(temperatures) - 2,
                    alpha=0.12, color="#3B8BD4")

    # ── Annotate highest and lowest temperatures ─────────────────────────────
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    max_idx  = temperatures.index(max_temp)
    min_idx  = temperatures.index(min_temp)

    ax.annotate(
        f"High: {max_temp}°C",
        xy=(timestamps[max_idx], max_temp),
        xytext=(10, 12), textcoords="offset points",
        fontsize=9, color="#C04828",
        arrowprops=dict(arrowstyle="->", color="#C04828", lw=1)
    )
    ax.annotate(
        f"Low: {min_temp}°C",
        xy=(timestamps[min_idx], min_temp),
        xytext=(10, -18), textcoords="offset points",
        fontsize=9, color="#1D6FAA",
        arrowprops=dict(arrowstyle="->", color="#1D6FAA", lw=1)
    )

    # ── Axes formatting ──────────────────────────────────────────────────────
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a\n%d %b\n%H:%M"))
    ax.set_title(
        f"4-Day Hourly Temperature Forecast — {forecast.city}, {forecast.country}",
        fontsize=13, fontweight="bold", pad=14
    )
    ax.set_ylabel("Temperature (°C)", fontsize=11)
    ax.set_xlabel("Date & Time", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.show()


def print_banner():
    """Prints the app banner on startup."""
    print("\n" + "="*44)
    print("         PyWeatherCLI")
    print("   Powered by OpenWeatherMap")
    print("="*44)


def get_valid_city():
    """
    Repeatedly prompts the user for a city name until a valid one is entered,
    or until the user types 'back'.
    Returns the city string, or None if the user wants to go back.
    """
    while True:
        city = input("\n  Enter city name (or 'back' to return): ").strip()

        if city.lower() == "back":
            return None
        elif len(city) < 2:
            print("  [!] Please enter a valid city name (at least 2 characters).")
        else:
            return city


# ==============================================================================
#  MAIN  —  interactive menu loop
# ==============================================================================

def main():
    print_banner()

    while True:
        print("\n  ── MENU ───────────────────────────────")
        print("  [1]  Current weather")
        print("  [2]  4-day forecast  (text)")
        print("  [3]  4-day forecast  (line graph)")
        print("  [0]  Quit")
        print("  ───────────────────────────────────────")

        choice = input("\n  Choose an option: ").strip()

        if choice == "0":
            print("\n  Goodbye! Stay weather-aware. 👋\n")
            break

        elif choice == "1":
            city = get_valid_city()
            if city is not None:
                weather = get_current_weather(city)
                if weather:
                    print(weather.to_display())
                    print(f"\n  Summary: {weather.summary()}")

        elif choice == "2":
            city = get_valid_city()
            if city is not None:
                forecast = get_forecast(city)
                if forecast:
                    display_forecast_text(forecast)

        elif choice == "3":
            city = get_valid_city()
            if city is not None:
                forecast = get_forecast(city)
                if forecast:
                    print(f"\n  Generating chart for {forecast.city}…")
                    plot_forecast(forecast)

        else:
            print("\n  [!] Invalid option. Please enter 0, 1, 2, or 3.")


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()