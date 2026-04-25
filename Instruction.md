# PyWeatherCLI — Student Task Instructions

> **Course:** Final Examination Project — Python Data Application with Visualization  
> **Group Size:** 8 students  
> **Source Reference:** `TheExample.py` (see also `weather_cli.py` as the full working reference)  
> **Goal:** Each student rewrites or debugs their assigned section. When all parts are combined, the result is a complete, working PyWeatherCLI application.

---

## How to Use These Instructions

1. Open `weather_cli.py` as your **reference**. Read through the entire file first so you understand how everything fits together.
2. Your individual part is listed below. Write your section inside `TheExample.py` **in the order the parts appear** (Part 1 goes first, Part 5 goes last).
3. Rewrite students must write the code **from scratch** based on the logic you see in the reference — do **not** copy-paste.
4. Debug students must **run, test, and find bugs** in the combined code and document every issue they find and fix.
5. Every student must follow the Programming Concept Requirements listed in the project brief.

---

## REWRITE STUDENTS (5 Students)

### ✏️ Student 1 — Imports, Configuration & `WeatherData` Class

**Lines in reference:** `weather_cli.py` lines 1–52

**Your tasks:**

- Add all required `import` statements at the top of `TheExample.py`:
  - `requests`, `json`, `datetime`, `matplotlib.pyplot`, `matplotlib.dates`
- Define the three configuration constants:
  - `API_KEY` — the OpenWeatherMap API key string
  - `BASE_URL` — the base URL `"https://api.openweathermap.org/data/2.5"`
  - `UNITS` — set to `"metric"`
- Create the `WeatherData` class with:
  - `__init__` that stores: `city`, `country`, `temp`, `feels_like`, `humidity`, `description`, `wind_speed`
  - `to_display()` method — returns a nicely formatted multi-line string showing all weather fields
  - `summary()` method — returns a single compact line (e.g. `"Manila: 31.2°C — Partly Cloudy"`)

**Concepts you must demonstrate:**
- Proper use of variables and identifiers
- A class with `__init__` and instance methods (**encapsulation**)
- Use of Python built-in modules

---

### ✏️ Student 2 — `ForecastData` Class (Inheritance)

**Lines in reference:** `weather_cli.py` lines 55–78

**Your tasks:**

- Create the `ForecastData` class that **inherits from `WeatherData`**
- In `__init__`:
  - Call `super().__init__(...)` with placeholder `None` values for weather fields
  - Initialize three empty lists: `self.timestamps`, `self.temperatures`, `self.descriptions`
- Write the `add_entry(self, timestamp, temp, description)` method — appends one 3-hour forecast slot to all three lists
- Write the `get_4day_slice(self)` method — returns the **first 32 entries** from each list as a tuple `(timestamps, temperatures, descriptions)`

**Concepts you must demonstrate:**
- **Inheritance** (`ForecastData` IS-A `WeatherData`)
- Calling the parent class constructor with `super()`
- Instance methods that modify and return instance data

---

### ✏️ Student 3 — API Fetch Functions

**Lines in reference:** `weather_cli.py` lines 85–156

**Your tasks:**

- Write `get_current_weather(city)`:
  - Build a `params` dict with `q`, `appid`, and `units` keys
  - Use `requests.get()` to call `{BASE_URL}/weather` with a 10-second timeout
  - On HTTP 200 → parse the JSON and return a `WeatherData` object
  - On HTTP 404 → print a "city not found" message and return `None`
  - On HTTP 401 → print an "invalid API key" message and return `None`
  - On other errors → print the status code and return `None`
  - Catch `requests.exceptions.ConnectionError` and `requests.exceptions.Timeout`
- Write `get_forecast(city)`:
  - Same structure as above but calls `{BASE_URL}/forecast`
  - On success → create a `ForecastData` object, loop over `data["list"]`, convert each `dt` timestamp with `datetime.datetime.fromtimestamp()`, and call `forecast.add_entry()` for each item
  - Return the populated `ForecastData` object

**Concepts you must demonstrate:**
- User-defined functions with parameters and return values
- `try/except` error handling
- Looping over API response data
- Use of the `requests` module

---

### ✏️ Student 4 — Text Display & User Input Functions

**Lines in reference:** `weather_cli.py` lines 159–274

**Your tasks:**

- Write `display_forecast_text(forecast)`:
  - Call `forecast.get_4day_slice()` to get timestamps, temperatures, and descriptions
  - Print a header showing the city and country
  - Use a `for` loop with `zip()` over all three lists
  - Use a **nested condition** to detect when the date changes and print a day header (e.g. `"Monday, Apr 28"`) only when the day is new
  - Print each time slot with the time, temperature, and condition
- Write `print_banner()`:
  - Prints the app title banner to the terminal on startup
- Write `get_valid_city()`:
  - Use a `while True` loop to repeatedly prompt the user
  - If the user types `"back"` (case-insensitive) → return `None`
  - If the input is fewer than 2 characters → print a validation message and loop again
  - Otherwise → return the city string

**Concepts you must demonstrate:**
- User-defined functions
- Nested conditions inside a loop
- `while` loop for input validation
- Formatted string output (`f-strings`)

---

### ✏️ Student 5 — Data Visualization (`plot_forecast`)

**Lines in reference:** `weather_cli.py` lines 189–249

**Your tasks:**

- Write `plot_forecast(forecast)`:
  - Call `forecast.get_4day_slice()` to get the data
  - If there are no timestamps → print an error message and `return`
  - Create a figure and axes using `plt.subplots(figsize=(13, 5))`
  - Plot a **line graph** of temperature over time using `ax.plot()` with:
    - A coloured line (`color`, `linewidth`)
    - Circle markers (`marker="o"`, `markersize`, `markerfacecolor`, `markeredgewidth`)
    - A legend label `"Temperature (°C)"`
  - Add a **shaded fill** under the line using `ax.fill_between()`
  - Annotate the **highest** and **lowest** temperatures on the chart using `ax.annotate()` with arrow properties
  - Format the x-axis with `mdates.HourLocator(interval=6)` and `mdates.DateFormatter()`
  - Set a descriptive chart title, x-label, y-label, and grid lines
  - Call `plt.tight_layout()` and `plt.show()`

**Concepts you must demonstrate:**
- Data visualization using **Matplotlib** (line graph required)
- Annotating a chart with high/low values
- Use of `matplotlib.dates` for time-axis formatting
- A user-defined function dedicated to visualization

---

## DEBUG STUDENTS (3 Students)

> **Instructions for all debug students:**
> - Run the combined `TheExample.py` file after the rewrite students have finished their sections.
> - Use print statements, `try/except`, or Python's built-in `pdb` debugger to trace issues.
> - Document every bug you find in a comment block at the top of your section using this format:
>   ```
>   # BUG FOUND: <short description>
>   # LOCATION: <function/class name, line number if known>
>   # FIX APPLIED: <what you changed and why>
>   ```
> - After fixing, re-run the program to confirm the bug is resolved.

---

### 🐛 Student 6 — Debug: Classes (`WeatherData` & `ForecastData`)

**Focus area:** Student 1's and Student 2's code — the two classes.

**What to test:**

| Test | Expected Behaviour |
|------|--------------------|
| Create a `WeatherData` object with sample values | `to_display()` prints all fields correctly |
| Call `summary()` | Returns a one-line string with city, temp, and description |
| Create a `ForecastData` object | Inherits from `WeatherData`, lists start empty |
| Call `add_entry()` multiple times | Each list grows by one item per call |
| Call `get_4day_slice()` with fewer than 32 entries | Returns only what is available (no crash) |
| Call `get_4day_slice()` with more than 32 entries | Returns exactly 32 entries, not more |

**Common bugs to look for:**
- Missing `self.` on instance attributes
- `super().__init__()` not receiving the correct number of arguments
- `get_4day_slice()` returning the wrong slice or raising an `IndexError`
- `to_display()` crashing if any field is `None`

---

### 🐛 Student 7 — Debug: API Fetch Functions (`get_current_weather` & `get_forecast`)

**Focus area:** Student 3's code — the two API functions.

**What to test:**

| Test | Expected Behaviour |
|------|--------------------|
| Valid city name (e.g. `"Manila"`) | Returns a `WeatherData` / `ForecastData` object |
| City name with mixed case (e.g. `"mANiLa"`) | API call still succeeds |
| Misspelled city (e.g. `"Maniila"`) | Prints "city not found" message, returns `None` |
| Empty string `""` passed as city | Handled gracefully — does not crash |
| Simulate no internet (disconnect Wi-Fi or disable network) | Prints "No internet connection" message |
| Invalid API key (change `API_KEY` temporarily) | Prints "Invalid API key" message |

**Common bugs to look for:**
- Missing `return None` at the end of the function (causes `None` to be returned implicitly — verify it is explicit)
- `datetime.datetime.fromtimestamp()` receiving wrong data type
- The loop in `get_forecast()` not calling `add_entry()` correctly
- `params` dict missing a required key (causes HTTP 400)
- Exception handling catching too broadly (`except Exception`) or not catching `Timeout`

---

### 🐛 Student 8 — Debug: Visualization & Main Menu Loop

**Focus area:** Student 5's `plot_forecast()` and the `main()` function connecting everything.

**What to test:**

| Test | Expected Behaviour |
|------|--------------------|
| Run the full program and choose option `[0]` | Prints goodbye message and exits cleanly |
| Choose option `[1]` with a valid city | Prints formatted current weather |
| Choose option `[2]` with a valid city | Prints day-by-day text forecast |
| Choose option `[3]` with a valid city | Opens a Matplotlib line chart window |
| Enter an invalid menu option (e.g. `"abc"`) | Prints "Invalid option" and loops back to menu |
| Type `"back"` when asked for a city | Returns to the main menu without crashing |
| Choose option `[3]` with a city that returns no forecast data | Prints an error message, does not crash |

**Common bugs to look for:**
- `main()` not calling `print_banner()` before the loop
- `choice` comparison failing due to leading/trailing whitespace (should use `.strip()`)
- `plot_forecast()` crashing when `temperatures` is an empty list (check for guard at the top)
- `ax.annotate()` failing if `timestamps` has only one element
- `plt.show()` never called, so the chart window never opens
- The `while True` loop in `main()` not having a `break` on choice `"0"`

---

## Submission Checklist

Before submitting, every student must verify their section meets these requirements:

- [ ] At least **two user-defined functions** are present in the combined file
- [ ] At least **one class** is defined (with `__init__` and methods)
- [ ] **Inheritance** is used (`ForecastData` extends `WeatherData`)
- [ ] **Control structures** are used (loops, nested conditions, `if/elif/else`)
- [ ] **Matplotlib** is used to produce at least one chart (line graph)
- [ ] **Input operations** prompt the user for data
- [ ] **Output operations** display results clearly to the terminal
- [ ] All bugs found by debug students are documented and fixed
- [ ] The program runs end-to-end without unhandled exceptions

---

## Quick-Start Reference

```
# Install required packages (run once)
pip install requests matplotlib

# Run the program
python TheExample.py
```

> **API Key Note:** The shared key in `TheExample.py` is for development/testing only.  
> Each student may register for a free personal key at https://openweathermap.org/api
