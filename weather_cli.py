import argparse
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import os

# --- Configuration ---
# Replace this string with your actual OpenWeatherMap API Key, 
# or set it as an environment variable: export OWM_API_KEY="your_key"
API_KEY = os.environ.get("OWM_API_KEY", "762474eb41860948079ca87d6030807f")

# --- 1. DATA FETCHING ---
def get_owm_forecast(city_name):
    """Fetches the 5-day / 3-hour forecast from OpenWeatherMap."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric"
    
    response = requests.get(url)
    
    # Handle the most common OWM error gracefully
    if response.status_code == 401:
        print("❌ Error: Unauthorized. Please check that your OpenWeatherMap API key is correct.")
        sys.exit(1)
    elif response.status_code == 404:
        print(f"❌ Error: Could not find city '{city_name}'.")
        sys.exit(1)
        
    response.raise_for_status()
    return response.json()

# --- 2. VISUALIZATION ---

def display_datetime():
    """Prints the current date and time cleanly."""
    now = datetime.now()
    print("-" * 45)
    print(f"📅 Date: {now.strftime('%A, %B %d, %Y')}")
    print(f"⏰ Time: {now.strftime('%I:%M %p')}")
    print("-" * 45)

def plot_continuous_forecast(city_name, weather_data):
    """Uses Matplotlib to graph the continuous 3-hour temperature intervals."""
    dates = []
    temps = []
    
    # OWM returns 40 intervals (5 days * 8 intervals/day). 
    # We slice the first 32 to get exactly 4 days of data.
    for item in weather_data['list'][:32]:
        # Convert OWM's string timestamp (YYYY-MM-DD HH:MM:SS) to a Python datetime object
        dt = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")
        dates.append(dt)
        temps.append(item['main']['temp'])

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, temps, color='#FF5733', marker='o', markersize=4, linewidth=2, label="Temp (°C)")

    # Styling the graph
    proper_city = weather_data['city']['name']
    country = weather_data['city']['country']
    plt.title(f"4-Day Continuous Temperature Forecast for {proper_city}, {country}", fontsize=14, pad=15)
    plt.ylabel("Temperature (°C)", fontsize=12)
    
    # Format the X-axis to show days clearly
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %I %p'))
    plt.xticks(rotation=45)
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout() # Prevents labels from getting cut off
    
    print(f"📈 Opening Matplotlib forecast window for {proper_city}...")
    plt.show()

# --- 3. ENTRY POINT ---

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  Warning: You are using the placeholder API key.")
        print("Please edit the script and insert your real OpenWeatherMap API key.\n")

    parser = argparse.ArgumentParser(description="Terminal Clock and OWM Weather Forecaster")
    parser.add_argument(
        "city",
        nargs="?",
        type=str,
        help="The name of the city (e.g., 'Tokyo' or 'Paris')",
    )
    args = parser.parse_args()

    city_name = args.city
    if not city_name:
        city_name = input("Input your city here: ").strip()
        if not city_name:
            print("❌ Error: City name cannot be empty.")
            sys.exit(1)

    display_datetime()
    print(f"🔍 Fetching data from OpenWeatherMap for: {city_name.title()}...")
    
    try:
        weather_data = get_owm_forecast(city_name)
        plot_continuous_forecast(city_name, weather_data)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: ({e})")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()