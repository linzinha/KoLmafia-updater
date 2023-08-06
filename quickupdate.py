import configparser
import hashlib
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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

# Updated STATES dictionary
STATES = {
    'True': {'status_indicator': 'Enabled', 'status_message': 'Enabled message'},
    'False': {'status_indicator': 'Disabled', 'status_message': 'Disabled message'},
    'None': {'status_indicator': 'Not Set', 'status_message': 'Not Set message'}
}


def set_config(config, key, value):
    config.set('DEFAULT', key, value)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        config.write(config_file)
        key = str(key).replace('_', ' ')
        print(f"{key} set to: {value}")


def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def run_updater(config, mafia_folder):
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("Fetching latest build - this can take a few seconds\n")
    result = None
    latest_jar_file = None
    new_jar_file = None
    existing_jar_file = None
    calculated_hash_downloaded_jar_file = None
    updater_script_path = os.path.abspath(__file__)  # kol_updater.py absolute path
    updater_script_directory = os.path.dirname(updater_script_path)  # kol_updater.py directory
    download_folder = os.path.join(updater_script_directory, 'file_handling')
    if not os.path.isdir(download_folder):  # Check if the 'file_handling' directory already exists
        os.mkdir(download_folder)
    else:
        print('')

    try:  # Retrieve the HTML content
        response = requests.get(URL)
        response.raise_for_status()  # Raise an exception for any HTTP error
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    new_jar_link = next(link['href'] for link in soup.find_all('a', href=True) if
                        link['href'].endswith('.jar'))

    if new_jar_link:
        new_jar_file = os.path.join(download_folder, os.path.basename(new_jar_link))
        new_file_name = str(new_jar_file.split("\\")[-1:])[2:-2]
        try:
            response = requests.get(URL + new_jar_link, stream=True)
            response.raise_for_status()  # Raise an exception for any HTTP error
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            exit(1)
        with open(new_jar_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

    if new_jar_file:
        calculated_hash_downloaded_jar_file = calculate_hash(new_jar_file)

    print("Analyzing current version")
    existing_jar_version = config.get('DEFAULT', 'jar_version', fallback='')
    existing_jar_hash = config.get('DEFAULT', 'jar_hash', fallback='')
    calculated_hash_existing_jar_file = 'Unset'
    try:  # If jar version is a number
        int(existing_jar_version)
        os.path.join(mafia_folder, f"KoLmafia-{existing_jar_version}")
        existing_jar_file = os.path.join(mafia_folder, f"KoLmafia-{existing_jar_version}.jar")
        # if the file the jar version references doesn't exist set working reference to all jar variables to None
        if not os.path.isfile(existing_jar_file):
            existing_jar_file = None
            existing_jar_version = None
            existing_jar_hash = None
            calculated_hash_existing_jar_file = "skip hash"
        else:  # if the file the jar version references does exist, check for stored Hash
            if existing_jar_hash is None:
                calculated_hash_existing_jar_file = "calculate jar"  # get hash from jar file
            else:
                calculated_hash_existing_jar_file = "use config"  # use existing, stored hash
    except ValueError as e:
        if existing_jar_version is None and existing_jar_hash is None:
            # Get a list of all JAR files in the mafia_folder
            existing_jar_files = [file for file in os.listdir(mafia_folder) if file.endswith('.jar')]
            # Sort the list based on the modification time (newest first)
            existing_jar_files.sort(key=lambda x: os.path.getmtime(os.path.join(mafia_folder, x)), reverse=True)
            existing_jar_file = existing_jar_files[0]
            calculated_hash_existing_jar_file = "calculate jar"

    match calculated_hash_existing_jar_file:
        case "use config":
            calculated_hash_existing_jar_file = existing_jar_hash
        case "calculate jar":
            calculated_hash_existing_jar_file = calculate_hash(existing_jar_file)
        case "skip hash":
            calculated_hash_existing_jar_file = None

    # Compare versions
    if calculated_hash_existing_jar_file == calculated_hash_downloaded_jar_file:
        result = "Mafia is already up to date:\n The downloaded file's hash matches the current file. Download removed."
        os.remove(new_jar_file)  # Remove the newly downloaded file as it is identical to the current one
        latest_jar_file = existing_jar_file

    else:
        # move new_jar_file to mafia_folder
        os.rename(new_jar_file, os.path.join(mafia_folder, os.path.basename(new_jar_file)))
        new_jar_file = os.path.join(mafia_folder, os.path.basename(new_jar_file))
        latest_jar_file = new_jar_file
        if calculated_hash_existing_jar_file is not None:
            result = f"New version of Mafia found, updating to version {new_jar_file[-9:-4]}."
        else:
            result = "No JAR files found in the folder - skipping file verification.\n "
            f"Mafia has been repaired and updated to version {new_jar_file[-9:-4]}."

    # Clean up mafia folder - get a list of all JAR files in the mafia_folder
    existing_jar_files = [file for file in os.listdir(mafia_folder) if file.endswith('.jar')]
    # Sort the list based on the modification time (newest first)
    existing_jar_files.sort(key=lambda x: os.path.getmtime(os.path.join(mafia_folder, x)), reverse=True)

    # Delete the rest of the JAR files (if any)
    if len(existing_jar_files) > 1:
        print("Cleaning up Mafia folder:")
        for jar_file in existing_jar_files[1:]:
            file_path = os.path.join(mafia_folder, jar_file)
            os.remove(file_path)
            print(f"Deleted {jar_file}")

    # Update the config file
    if latest_jar_file != existing_jar_file:
        set_config(config, 'last_updated', str(datetime.now()))
    config.set('DEFAULT', 'last_run', current_datetime)
    config.set('DEFAULT', 'jar_version', latest_jar_file[-9:-4])
    config.set('DEFAULT', 'jar_hash', calculate_hash(latest_jar_file))
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config.write(config_file)

    print(f"\n{result}")
    exit(1)


# Main function
def main():
    config = configparser.ConfigParser(defaults=CONFIG_DEFAULTS)
    # Check if config.ini exists, if not, create it with the default path
    if not os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'w') as config_file:
            config.write(config_file)
    # Read the configuration from the file
    config.read(CONFIG_FILE_PATH)
    mafia_folder = config.get('DEFAULT', 'destination_folder', fallback='Not Set')

    while True:
        run_updater(config, mafia_folder)


if __name__ == "__main__":
    main()
