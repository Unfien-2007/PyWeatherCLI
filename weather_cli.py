import argparse
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import sys
import os

# --- Configuration ---
API_KEY = os.environ.get("OWM_API_KEY", "762474eb41860948079ca87d6030807f")

FORECAST_URL        = "https://api.openweathermap.org/data/2.5/forecast"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
GEO_DIRECT_URL      = "https://api.openweathermap.org/geo/1.0/direct"

# ── Design tokens ────────────────────────────────────────────────────────────
C = {
    "fig_bg":      "#F0F4F8",   # outer figure background
    "panel_bg":    "#FFFFFF",   # forecast subplot face
    "card_bg":     "#FFFFFF",   # stat card face

    # Warm orange for the forecast line (stands out against blues)
    "line":        "#F97316",
    "line_fill":   "#FED7AA",

    # Neutral text
    "text_h":      "#0F172A",
    "text_body":   "#334155",
    "text_muted":  "#94A3B8",

    "grid":        "#E2E8F0",
    "spine":       "#CBD5E1",

    # Per-card top-stripe colours (temp, feels-like, humidity, wind)
    "card_colors": ["#F97316", "#FB923C", "#3B82F6", "#06B6D4"],
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _remove_all_spines(ax):
    for sp in ax.spines.values():
        sp.set_visible(False)


def _card_frame(ax, accent_color):
    """Style an axis as a clean white card with a coloured top stripe."""
    ax.set_facecolor(C["card_bg"])
    _remove_all_spines(ax)
    ax.set_xticks([])
    ax.set_yticks([])
    # Coloured stripe across the top
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 0.88), 1, 0.12,
        boxstyle="square,pad=0",
        transform=ax.transAxes,
        facecolor=accent_color,
        edgecolor="none",
        clip_on=False,
        zorder=4,
    ))


# ── 1. Data fetching ─────────────────────────────────────────────────────────

def handle_api_status(response):
    if response.status_code == 401:
        raise PermissionError(
            "Unauthorized. Check your OpenWeatherMap API key."
        )


def get_owm_forecast(city_name):
    params = {"q": city_name, "appid": API_KEY, "units": "metric"}
    r = requests.get(FORECAST_URL, params=params, timeout=10)
    handle_api_status(r)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def get_current_weather(city_name):
    params = {"q": city_name, "appid": API_KEY, "units": "metric"}
    r = requests.get(CURRENT_WEATHER_URL, params=params, timeout=10)
    handle_api_status(r)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def get_city_suggestions(city_name, limit=5):
    params = {"q": city_name, "limit": limit, "appid": API_KEY}
    r = requests.get(GEO_DIRECT_URL, params=params, timeout=10)
    handle_api_status(r)
    r.raise_for_status()
    return r.json()


def format_city_suggestions(suggestions):
    labels = []
    for item in suggestions:
        name    = item.get("name", "Unknown")
        state   = item.get("state")
        country = item.get("country", "")
        labels.append(
            f"{name}, {state}, {country}" if state else f"{name}, {country}"
        )
    return list(dict.fromkeys(labels))


# ── 2. Visualisation ─────────────────────────────────────────────────────────

def display_datetime():
    now = datetime.now()
    print("-" * 45)
    print(f"📅 Date: {now.strftime('%A, %B %d, %Y')}")
    print(f"⏰ Time: {now.strftime('%I:%M %p')}")
    print("-" * 45)


def plot_forecast(ax, weather_data):
    """
    Line + shaded-fill forecast chart.
    Features:
      · Orange line on a white panel so it reads clearly
      · Hollow circle markers
      · Shaded fill between line and floor
      · Dotted day-separator verticals
      · Peak & trough value annotations
    """
    dates, temps = [], []
    for item in weather_data["list"][:32]:      # 4 days × 8 intervals
        dates.append(datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S"))
        temps.append(item["main"]["temp"])

    # Panel base style
    ax.set_facecolor(C["panel_bg"])
    _remove_all_spines(ax)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color(C["spine"])
    ax.yaxis.grid(True, color=C["grid"], linewidth=0.7, linestyle="--")
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0,
                   labelsize=8, labelcolor=C["text_muted"])

    # Shaded fill
    floor = min(temps) - 1
    ax.fill_between(dates, temps, floor,
                    color=C["line_fill"], alpha=0.55, zorder=1)

    # Main line
    ax.plot(dates, temps,
            color=C["line"], linewidth=2.2,
            marker="o", markersize=4,
            markerfacecolor=C["panel_bg"],
            markeredgewidth=1.8, markeredgecolor=C["line"],
            zorder=3, label="Temperature (°C)")

    # Day-separator verticals
    seen = set()
    for d in dates:
        day = d.strftime("%Y-%m-%d")
        if day not in seen:
            seen.add(day)
            ax.axvline(d, color=C["grid"], linewidth=1,
                       linestyle=":", zorder=2)

    # Annotate global peak and trough only
    peak_i   = temps.index(max(temps))
    trough_i = temps.index(min(temps))
    for i, va in [(peak_i, "bottom"), (trough_i, "top")]:
        offset = 9 if va == "bottom" else -9
        ax.annotate(
            f"{temps[i]:.1f}°",
            xy=(dates[i], temps[i]),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center", va=va,
            fontsize=7.5, fontweight="bold", color=C["line"],
        )

    # Axes labels & title
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %I %p"))
    ax.tick_params(axis="x", rotation=35)

    city    = weather_data["city"]["name"]
    country = weather_data["city"]["country"]
    ax.set_title(
        f"4-Day Temperature Forecast  ·  {city}, {country}",
        fontsize=11, pad=10, loc="left",
        fontweight="bold", color=C["text_h"],
    )
    ax.set_ylabel("°C", fontsize=9, color=C["text_muted"], labelpad=6)
    ax.legend(fontsize=8, frameon=False,
              labelcolor=C["text_muted"], loc="upper right")


def plot_stat_cards(card_axes, weather_data):
    """
    Four card-style subplots replacing the original mixed-scale bar chart.
    Each card shows: coloured top stripe · large value · unit · metric label.
    """
    main = weather_data.get("main", {})
    wind = weather_data.get("wind", {})
    desc = (weather_data.get("weather", [{}])[0]
            .get("description", "N/A").title())

    METRICS = [
        ("Temperature", f"{main.get('temp', 0):.1f}",    "°C",  C["card_colors"][0]),
        ("Feels Like",  f"{main.get('feels_like', 0):.1f}", "°C", C["card_colors"][1]),
        ("Humidity",    f"{main.get('humidity', 0):.0f}", "%",   C["card_colors"][2]),
        ("Wind Speed",  f"{wind.get('speed', 0):.1f}",   "m/s", C["card_colors"][3]),
    ]

    for ax, (label, value, unit, accent) in zip(card_axes, METRICS):
        _card_frame(ax, accent)

        # Large value
        ax.text(0.5, 0.52, value,
                transform=ax.transAxes,
                ha="center", va="center",
                fontsize=26, fontweight="bold",
                color=C["text_h"])

        # Unit
        ax.text(0.5, 0.30, unit,
                transform=ax.transAxes,
                ha="center", va="center",
                fontsize=10, color=C["text_muted"])

        # Metric label
        ax.text(0.5, 0.10, label,
                transform=ax.transAxes,
                ha="center", va="center",
                fontsize=8.5, fontweight="bold",
                color=C["text_body"])

    # Stash condition on first card for figure-level placement
    card_axes[0]._weather_condition = desc


def plot_weather_dashboard(forecast_data, current_weather):
    """
    Assembles everything into one figure.

    GridSpec layout:
      Row 0 (60 %): forecast line chart — spans all 4 columns
      Row 1 (40 %): 4 stat cards       — one per column
    """
    city    = forecast_data["city"]["name"]
    country = forecast_data["city"]["country"]
    now_str = datetime.now().strftime("%A, %B %d, %Y  ·  %I:%M %p")

    fig = plt.figure(figsize=(14, 8.5), facecolor=C["fig_bg"])

    gs = GridSpec(
        2, 4,
        figure=fig,
        height_ratios=[1.6, 1],
        hspace=0.38,
        wspace=0.18,
        top=0.86,
        bottom=0.11,
        left=0.06,
        right=0.97,
    )

    ax_forecast = fig.add_subplot(gs[0, :])
    card_axes   = [fig.add_subplot(gs[1, c]) for c in range(4)]

    plot_forecast(ax_forecast, forecast_data)
    plot_stat_cards(card_axes, current_weather)

    # ── Figure header ────────────────────────────────────────────────────────
    fig.text(0.06, 0.955,
             "Weather Dashboard",
             fontsize=20, fontweight="bold",
             color=C["text_h"], va="bottom")

    fig.text(0.06, 0.920,
             f"{city}, {country}",
             fontsize=11, color=C["text_muted"], va="bottom")

    # Thin rule below header
    line = plt.Line2D(
        [0.06, 0.97], [0.915, 0.915],
        transform=fig.transFigure,
        color=C["spine"], linewidth=0.8,
    )
    fig.add_artist(line)

    # ── Condition badge centred below cards ──────────────────────────────────
    condition = getattr(card_axes[0], "_weather_condition", "")
    fig.text(0.515, 0.030,
             f"☁  Current condition:  {condition}",
             ha="center", va="bottom",
             fontsize=9, color=C["text_muted"])

    # ── Timestamp bottom-right ───────────────────────────────────────────────
    fig.text(0.97, 0.005,
             f"Generated {now_str}",
             ha="right", va="bottom",
             fontsize=7.5, color=C["text_muted"])

    return fig


# ── 3. Entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Terminal Clock and OWM Weather Forecaster"
    )
    parser.add_argument("city", nargs="?", type=str,
                        help="City name (e.g. 'Tokyo' or 'Paris')")
    args = parser.parse_args()

    city_name = args.city
    if not city_name:
        city_name = input("Input your city here: ").strip()
        if not city_name:
            print("❌ Error: City name cannot be empty.")
            sys.exit(1)

    try:
        while True:
            display_datetime()
            print(f"🔍 Fetching data from OpenWeatherMap for: {city_name.title()}...")

            forecast_data = get_owm_forecast(city_name)
            if forecast_data is not None:
                break

            print(f"❌ Could not find city '{city_name}'.")
            suggestions = get_city_suggestions(city_name)
            labels      = format_city_suggestions(suggestions)

            if labels:
                print("💡 Did you mean one of these?")
                for idx, label in enumerate(labels, start=1):
                    print(f"   {idx}. {label}")

            city_name = input("Try another city (or press Enter to quit): ").strip()
            if not city_name:
                print("👋 Exiting without fetching weather data.")
                return

        current_weather = get_current_weather(city_name)
        if current_weather is None:
            print("❌ Could not fetch current weather for the selected city.")
            return

        plot_weather_dashboard(forecast_data, current_weather)

        proper_city = forecast_data["city"]["name"]
        print(f"📈 Opening weather dashboard for {proper_city}...")
        plt.show()

    except PermissionError as e:
        print(f"❌ Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()