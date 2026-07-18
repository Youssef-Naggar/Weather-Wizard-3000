# Weather Wizard 3000 🌦️

A personal weather forecasting assistant with dynamic, verified AI-powered outfit recommendations, engineered in Python using clean MVC and Command pattern architectures.

---

## 📋 Overview

Weather Wizard 3000 is an interactive CLI application that provides weather forecasts and highly personalized clothing/comfort recommendations. 

The application fetches real-time forecast data via the OpenWeatherMap API, resolves coordinate lookups via multiple geolocation providers, and dynamically prompts LLMs via **LiteLLM** to suggest appropriate styling choices matching the user's demographic profile, climate sensitivities, style preferences, and current commute requirements.

---

## ✨ Features

- **5-Day Weather Forecast:** Detailed insights into maximum, minimum, and feels-like temperatures, average humidity, and rain forecasts.
- **Multiple Geolocation Options:**
  - Automated location detection using IP coordinates (with fallback support).
  - Search by city name.
  - Manual coordinate inputs (latitude and longitude).
- **Universal LLM Setup (SDK-Agnostic):** Dynamically configure and switch model routing to any supported provider in **LiteLLM** (OpenAI, Anthropic, Gemini, Groq, Cohere, Ollama, etc.) directly from the settings menu.
- **Hermes-Style Live Verification:** Credentials and routing are validated via a live test call to the LLM before any configuration changes are written to `model-settings.json`.
- **Personalized Recommendations:**
  - Configurable comfort settings (cold thresholds, hot thresholds, perfect temperature).
  - Style configurations (style profile, favorite colors).
  - Trip-specific parameters asked dynamically (commute transit mode, dress codes, trip purpose).

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Active OpenWeatherMap API key (set as `OWM_API_KEY` in environment variables or `.env` file)
- API credentials for your chosen LLM provider (configured securely at runtime)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/weather-wizard-3000.git
   cd weather-wizard-3000
   ```

2. Install core dependencies:
   ```bash
   pip install requests litellm prettytable pydantic python-dotenv
   ```

3. (Optional) Install development and testing dependencies:
   ```bash
   pip install pytest pytest-cov ruff pyrefly bandit radon xenon
   ```

4. Create a `.env` file in the root directory and configure your OpenWeatherMap API Key:
   ```env
   OWM_API_KEY="your_openweathermap_api_key"
   ```

### Usage

Run the bootstrap script to start the CLI interface:
```bash
python main.py
```

---

## 🏗️ Architecture & Project Structure

The project strictly follows the **Model-View-Controller (MVC)** and **Command Patterns** to ensure concerns remain decoupled:

```text
weather-wizard-3000/
├── main.py              # Boots and runs the WeatherApp controller
├── controller.py        # Orchestrates control loops and registers Command classes
├── ui.py                # Handles all input collection, grid layouts, and CLI menus
├── forecast.py          # Handles weather processing logic and OpenWeatherMap clients
├── brain.py             # Executes calls and test checks to LiteLLM completion API
├── prompt_builder.py    # Manages user profiles, model validation, and system prompt compilations
├── prompts.py           # Contains system templates and mock assistant response fixtures
├── exceptions.py        # Defines domain-specific validation and setting errors
└── utilities.py         # Includes geolocation provider registries and kelvin conversions
```

- **Model Layer:** `Forecast` (domain entity containing weather metrics) and `WeatherClient` (HTTP fetcher).
- **View Layer:** `WeatherUI` (CLI layout grids and user prompts).
- **Controller Layer:** `WeatherApp` (coordinates loops) and `Command` classes (encapsulates operations like `CitySearchCommand` or `SettingsCommand`).
- **Service Layer:** `Brain` (AI interfaces) and `prompt_builder` (profile serialization).

---

## 🛡️ Testing & Static Verification

The project includes a robust pipeline to verify styling, typing, security, complexity, and coverage:

- **Unit Testing:** Powered by `pytest` under the `tests/` directory. Run via:
  ```bash
  pytest
  ```
- **Linting & Formatting:** Strict checks via `ruff`. Run via:
  ```bash
  ruff check .
  ```
- **Type Checking:** Run checks via `pyrefly`:
  ```bash
  pyrefly check brain.py prompt_builder.py ui.py controller.py tests/
  ```
- **Security Audits:** Scan with `bandit` (ignoring testing asserts):
  ```bash
  bandit brain.py prompt_builder.py ui.py controller.py forecast.py exceptions.py main.py utilities.py
  ```
- **Complexity Checks:** Max absolute cyclomatic complexity verified under Radon and Xenon:
  ```bash
  xenon --max-absolute C --max-modules B --max-average A .
  ```
