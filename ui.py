import datetime

class WeatherUI:
    def print_welcome(self) -> None:
        print("\n=== 🌦️ Weather Wizard 3000 🌈 ===")
        print("Your personal weather forecasting assistant!\n")

    def print_time_menu(self, today: datetime.date) -> None:
        print("\n-------- Main Menu --------")
        print("1. Today")
        print("2. Tomorrow")
        print(f"3. {today + datetime.timedelta(days=2)}")
        print(f"4. {today + datetime.timedelta(days=3)}")
        print(f"5. {today + datetime.timedelta(days=4)}")
        print("6. Exit")
        print("Enter your choice (1-6): ", end="")

    def print_location_menu(self) -> None:
        print("\nChoose one of the following search methods:")
        print("1. Search by city name")
        print("2. Use my current location")
        print("3. Enter coordinates manually")
        print("4. Exit")
        print("Enter your choice (1-4): ", end="")

    def print_ai_menu(self) -> None:
        print("Do you want our AI Weather Wizard 3000 help you to dress properly in this weather?")
        print("1. Yes")
        print("2. No")
        print("Enter your choice (1-2): ", end="")

    def get_choice(self) -> int:
        try:
            return int(input().strip())
        except ValueError:
            return -1

    def get_city_name(self) -> str:
        print("\nEnter city name (e.g., Tokyo): ", end="")
        return input().strip()

    def get_coordinate(self, coord_type: str) -> float:
        range_str = "(-90 to 90)" if coord_type.lower() == "latitude" else "(-180 to 180)"
        print(f"\nEnter {coord_type.lower()} {range_str}: ", end="")
        while True:
            try:
                return float(input().strip())
            except ValueError:
                print(f"Invalid {coord_type.lower()}! Please enter a valid number: ", end="")

    def print_message(self, message: str) -> None:
        print(message)

    def print_error(self, message: str) -> None:
        print(f"⚠️  {message}")
