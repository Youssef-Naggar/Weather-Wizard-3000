from controller import WeatherApp

if __name__ == "__main__":
    app = WeatherApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
