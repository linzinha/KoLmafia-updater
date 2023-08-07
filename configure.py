import configparser
import os
import sys

# Constants
CONFIG_FILE_PATH = "config.ini"  # File path for the configuration file
STARTING_PATH = os.path.expanduser("~")  # Starting path for the script execution
KOLMAFIA_BUILD_URL = 'https://ci.kolmafia.us/job/Kolmafia/lastSuccessfulBuild/'
RESPONSE_OPTIONS = {'YES_OPTIONS': ['y', 'yes'], 'NO_OPTIONS': ['n', 'no'], 'CANCEL_OPTIONS': ['c', 'cancel']}
DEFAULT_CONFIG = {
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


def main_menu(config):
    while True:
        # Fetch the destination folder from the configuration
        mafia_folder = config.get('DEFAULT', 'destination_folder', fallback='Not Set')

        print("\nMenu:")
        print(f"1: Set destination folder [CURRENTLY {mafia_folder}]")
        print(f"2: Restore Config Defaults")
        print("0: Exit\n")

        choice = input("Enter your choice: ")

        match choice:
            case "1":
                mafia_folder = set_destination_folder(config)
            case "2":
                restore_defaults()
            case "3":
                print("configure_auto_updater is in development")
            case "0":
                sys.exit()
            case "_":
                print("Invalid choice. Please try again.")


def restore_defaults():
    config = configparser.ConfigParser()
    config['DEFAULT'] = DEFAULT_CONFIG
    with open(CONFIG_FILE_PATH, 'x') as config_file:
        config.write(config_file)


def set_config(config, key, value):
    config.set('DEFAULT', key, value)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        config.write(config_file)
        key = str(key).replace('_', ' ')
        print(f"{key} set to: {value}")


def set_destination_folder(config):
    DESTINATION_FOLDER = config['DEFAULT']['destination_folder'].strip()
    while True:
        folder_path = input(f"\nEnter the destination folder path (or c to [c]ancel)\n"
                            f"--------------\n"
                            f"Current Destination Folder Path: {DESTINATION_FOLDER}\n"
                            f"--------------\n"
                            f"Set New Destination Folder Path: {STARTING_PATH}\\").strip()
        if folder_path.lower() in RESPONSE_OPTIONS['CANCEL_OPTIONS']:
            return DESTINATION_FOLDER
        mafia_folder = os.path.join(STARTING_PATH, folder_path)
        if os.path.isdir(mafia_folder):
            verify = input(f"\nYou entered {mafia_folder}, is this correct? ([y]es/[n]o/[c]ancel): ")
            match verify[0].lower():
                case 'y':
                    set_config(config, 'destination_folder', mafia_folder)
                    main_menu(config)
                case 'n':
                    set_destination_folder(config)
                case 'c':
                    main_menu(config)
        else:
            print(f"{mafia_folder}\n"
                  "is an Invalid folder path. Please enter a valid existing folder path.")


# Main function
def main():
    # Read the configuration from the file
    config = configparser.ConfigParser(defaults=DEFAULT_CONFIG)
    config.read(CONFIG_FILE_PATH)

    while True:
        main_menu(config)


if __name__ == "__main__":
    main()
