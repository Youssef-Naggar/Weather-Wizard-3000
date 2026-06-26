import datetime
from typing import List
from utilities import get_auto_location
from forecast import Forecast
from brain import Brain


class Main:
    def __init__(self) -> None:
        self.weather_app = Forecast()
        self.wizard = Brain()
        self.weather_summary = ""

    def run(self) -> None:
        print("\n=== 🌦️ Weather Wizard 3000 🌈 ===")
        print("Your personal weather forecasting assistant!\n")

        while True:
            date: datetime.date = datetime.date.today()
            choice: int = 0
            retry: bool = False

            # Time selection menu
            while True:
                self.print_menu_time()
                retry = False
                choice = self.get_menu_choice()

                if choice == 1:
                    date = datetime.date.today()
                elif choice == 2:
                    date = datetime.date.today() + datetime.timedelta(days=1)
                elif choice == 3:
                    date = datetime.date.today() + datetime.timedelta(days=2)
                elif choice == 4:
                    date = datetime.date.today() + datetime.timedelta(days=3)
                elif choice == 5:
                    date = datetime.date.today() + datetime.timedelta(days=4)
                elif choice == 6:
                    self.exit_program()
                    return
                else:
                    print("⚠️  Invalid option! Please try again.")
                    retry = True

                if not retry:
                    break

            # Location selection menu
            retry = False
            while True:
                self.print_menu_location()
                choice = self.get_menu_choice()

                if choice == 1:
                    retry = self.handle_city_search(date)
                elif choice == 2:
                    retry = self.handle_auto_location(date)
                elif choice == 3:
                    retry = self.handle_manual_coordinates(date)
                elif choice == 4:
                    self.exit_program()
                    return
                else:
                    print("⚠️  Invalid option! Please try again.")
                    retry = True

                if not retry:
                    break

            # AI suggestion menu
            retry = False
            while True:
                self.print_menu_ai()
                choice = self.get_menu_choice()

                if choice == 1:
                    print(self.wizard.ai_suggestion(self.weather_summary))
                    break
                elif choice == 2:
                    break
                else:
                    print("⚠️  Invalid option! Please try again.")
                    retry = True

    def print_menu_ai(self) -> None:
        print("Do you want our AI Weather Wizard 3000 help you to dress properly in this weather?")
        print("1. Yes")
        print("2. No")

    def print_menu_time(self) -> None:
        today: datetime.date = datetime.date.today()
        print("\n-------- Main Menu --------")
        print("1. Today")
        print("2. Tomorrow")
        print(f"3. {today + datetime.timedelta(days=2)}")
        print(f"4. {today + datetime.timedelta(days=3)}")
        print(f"5. {today + datetime.timedelta(days=4)}")
        print("6. Exit")
        print("Enter your choice (1-6): ", end="")

    def print_menu_location(self) -> None:
        print("\nChoose one of the following search methods:")
        print("1. Search by city name")
        print("2. Use my current location")
        print("3. Enter coordinates manually")
        print("4. Exit")
        print("Enter your choice (1-4): ", end="")

    def get_menu_choice(self) -> int:
        try:
            return int(input())
        except ValueError:
            return -1

    def handle_city_search(self, target_date: datetime.date) -> bool:
        print("\nEnter city name (e.g., Tokyo): ", end="")
        city: str = input().strip()

        try:
            self.weather_app.fetch_weather_data_with_city_name(city, target_date)
            self.weather_summary = self.weather_app.get_weather_message()
            print("\n" + self.weather_summary)
            return False
        except Exception as e:
            print(f"⛈️  Failed to fetch data: {str(e)}")
            return True

    def handle_auto_location(self, target_date: datetime.date) -> bool:
        print("\n🔍 Detecting your location...")
        try:
            coords: List[float] = get_auto_location()
            print(f"📍 Detected coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
            self.weather_app.fetch_weather_data(coords[0], coords[1], target_date)
            self.weather_summary = self.weather_app.get_weather_message()
            print("\n" + self.weather_summary)
            return False
        except Exception as e:
            print(f"🌩️  Location detection failed: {str(e)}")
            return True

    def handle_manual_coordinates(self, target_date: datetime.date) -> bool:
        try:
            print("\nEnter latitude (-90 to 90): ", end="")
            lat: float = self.parse_coordinate("Latitude")

            print("Enter longitude (-180 to 180): ", end="")
            lon: float = self.parse_coordinate("Longitude")

            if self.is_valid_coordinate(lat, -90, 90) and self.is_valid_coordinate(lon, -180, 180):
                self.weather_app.fetch_weather_data(lat, lon, target_date)
                self.weather_summary = self.weather_app.get_weather_message()
                print("\n" + self.weather_summary)
            else:
                print("❌  Invalid coordinates! Values out of range.")
            return False
        except Exception as e:
            print(f"🌧️  Error: {str(e)}")
            return True

    def parse_coordinate(self, coord_type: str) -> float:
        while True:
            try:
                return float(input().strip())
            except ValueError:
                print(f"Invalid {coord_type.lower()}! Please enter a valid number: ", end="")

    def is_valid_coordinate(self, value: float, min_val: float, max_val: float) -> bool:
        return min_val <= value <= max_val

    def exit_program(self) -> None:
        print("\n✨ Thank you for using Weather Wizard 3000!")
        print("☁️  Stay dry and have a wonderful day!\n")


if __name__ == "__main__":
    app: Main = Main()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
