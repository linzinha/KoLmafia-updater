import configparser
import os
import sys
import configure
import update

# Constants
CONFIG_FILE_PATH = "config.ini"
STARTING_PATH = os.path.expanduser("~")
URL = 'https://ci.kolmafia.us/job/Kolmafia/lastSuccessfulBuild/'
OPTIONS = {'YES_OPTIONS': ['y', 'yes'], 'NO_OPTIONS': ['n', 'no'], 'CANCEL_OPTIONS': ['c', 'cancel']}
CONFIG_DEFAULTS = {
    'status': 'False',
    'scheduler_type': 'None',
    'destination_folder': STARTING_PATH,
    'last_run': '',
    'interval': '1',
    'startup_trigger': 'False',
    'time_trigger': 'False',
    'interval_trigger': 'False',
    'last_updated': '',
    'jar_version': '',
    'jar_hash': ''
}

# Check if config.ini exists, if not, create it with the default path
if not os.path.exists(CONFIG_FILE_PATH):
    configure.restore_defaults()


# Function to handle the main menu and user choices
def main_menu(config):
    while True:
        # Fetch the destination folder from the configuration
        mafia_folder = config.get('DEFAULT', 'destination_folder', fallback='Not Set')

        print("\nMenu:")
        print(f"1: Set destination folder [CURRENTLY {mafia_folder}]")
        print(f"2: Run updater")
        print(f"3: Configure automatic updater [IN DEVELOPMENT]")
        print("0: Exit\n")

        choice = input("Enter your choice: ")

        match choice:
            case "1":
                mafia_folder = configure.set_destination_folder(config)
            case "2":
                update.update_kolmafia_jar(config, mafia_folder)
            case "3":
                print("configure_auto_updater is in development")
            case "0":
                sys.exit()
            case "_":
                print("Invalid choice. Please try again.")


# Main function
def main():
    # Read the configuration from the file
    config = configparser.ConfigParser(defaults=CONFIG_DEFAULTS)
    config.read(CONFIG_FILE_PATH)

    while True:
        main_menu(config)


if __name__ == "__main__":
    main()
