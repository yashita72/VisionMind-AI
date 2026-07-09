from backend.config.settings import settings


def main():
    print(f"Starting {settings.APP_NAME}")
    print(f"Version: {settings.VERSION}")


if __name__ == "__main__":
    main()