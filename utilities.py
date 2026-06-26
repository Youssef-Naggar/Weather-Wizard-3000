from typing import Dict, List, Any
import requests

DEFAULT_COORDINATES = [46.947975, 7.447447]

def convert_kelvin_to_celsius_fahrenheit(kelvin: float) -> List[float]:
    celsius: float = kelvin - 273.15
    fahrenheit: float = celsius * 9 / 5 + 32
    return [celsius, fahrenheit]


def make_api_request(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    response: requests.Response = requests.get(url, params=params, timeout=10.0)
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")
    return response.json()


def get_auto_location() -> List[float]:
    providers = [
        {
            "name": "ipapi.co",
            "url": "https://ipapi.co/json/",
            "parser": lambda data: [float(data["latitude"]), float(data["longitude"])]
        },
        {
            "name": "ip-api.com",
            "url": "http://ip-api.com/json",
            "parser": lambda data: [float(data["lat"]), float(data["lon"])]
        },
        {
            "name": "ipinfo.io",
            "url": "https://ipinfo.io/json",
            "parser": lambda data: [float(coord) for coord in data["loc"].split(",")]
        }
    ]

    for provider in providers:
        try:
            response: requests.Response = requests.get(provider["url"], timeout=10.0)

            if response.status_code != 200:
                raise Exception(f"HTTP Status {response.status_code}")

            data: Dict[str, Any] = response.json()

            if provider["name"] == "ip-api.com" and data.get("status") == "fail":
                raise Exception(f"API failure: {data.get('message', 'Unknown error')}")

            coordinates = provider["parser"](data)
            print(f"✅ Location successfully captured using {provider['name']}!")
            return coordinates

        except (requests.RequestException, KeyError, ValueError) as err:
            print(f"⚠️ Geolocation provider {provider['name']} failed: {str(err)}")
            continue

    print("🚨 All location APIs failed. Falling back to default coordinates.")
    return DEFAULT_COORDINATES