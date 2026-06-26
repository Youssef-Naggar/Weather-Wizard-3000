from typing import Dict, List, Any
import requests

def convert_kelvin_to_celsius_fahrenheit(kelvin: float) -> List[float]:
    celsius: float = kelvin - 273.15
    fahrenheit: float = celsius * 9 / 5 + 32
    return [celsius, fahrenheit]


def make_api_request(url_string: str) -> Dict[str, Any]:
    response: requests.Response = requests.get(url_string)
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")
    return response.json()


def get_auto_location() -> List[float]:
    # Define the APIs, their endpoints, and custom parsing rules for each
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
            response: requests.Response = requests.get(provider["url"], timeout=5)

            if response.status_code != 200:
                raise Exception(f"HTTP Status {response.status_code}")

            data: Dict[str, Any] = response.json()

            # Special case: ip-api.com sends errors inside a 200 OK response body
            if provider["name"] == "ip-api.com" and data.get("status") == "fail":
                raise Exception(f"API failure: {data.get('message', 'Unknown error')}")

            # Extract coordinates using the provider's specific lambda parser
            coordinates = provider["parser"](data)
            print(f"✅ Location successfully captured using {provider['name']}!")
            return coordinates

        except Exception as e:
            continue  # Proceed to the next API in the list

    # Final safeguard if all three endpoints fail
    print("🚨 All location APIs failed. Falling back to default coordinates.")
    return [46.947975, 7.447447]