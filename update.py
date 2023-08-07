import configparser
import configure
import hashgen
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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


def set_configs(config, config_changes):
    """ ######################################################################
    Sets multiple configuration values and updates the config file.
    Args:   config (configparser.ConfigParser): Configuration object
            config_changes (dict): Dictionary containing key-value pairs to set in the config file
    ####################################################################### """
    for key, value in config_changes.items():
        config.set('DEFAULT', key, value)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        config.write(config_file)
    for key, value in config_changes.items():
        print(f"{key} set to: {value}")


def verify_configuration(config, mafia_folder):
    """ ######################################################################
    Verifies the configuration file and extracts version and hash information.
    Args:       config (configparser.ConfigParser): Configuration object
    Returns:    dict: Dictionary containing 'version', 'hash', and 'jar_file' information
    ####################################################################### """
    default_values = {
        'version': [int, config.get('DEFAULT', 'jar_version', fallback=''), 10],
        'hash': [int, config.get('DEFAULT', 'jar_hash', fallback=''), 16]
    }

    config_info = {}
    for key, value in default_values.items():
        try:
            config_info[key] = value[0](value[1], value[2])
        except (ValueError, TypeError):
            config_info[key] = None
    if not os.path.isfile(os.path.join(mafia_folder, f"KoLmafia-{config_info['version']}.jar")):
        config_info['jfile'] = None
    else:
        config_info['jfile'] = f"KoLmafia-{config_info['version']}.jar"
    return {"version": config_info['version'], "hash": config_info['hash'], "jar_file": config_info['jfile']}


def download_and_update_kolmafia_jar(config, mafia_folder, download_url, url_hash):
    """ ######################################################################
    Downloads and updates the Kolmafia JAR file.
    Args:       config (configparser.ConfigParser): Configuration object
                mafia_folder (str): Folder path where the JAR file will be saved
                download_url (str): URL to download the JAR file from
                url_hash (str): Hash value of the downloaded file
    Returns:    str: The version of the updated JAR file
    ####################################################################### """
    new_jar_file_path = os.path.join(mafia_folder, os.path.basename(download_url))
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Raise an exception for any HTTP error
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        exit(1)
    with open(new_jar_file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

    update_config = {
        'last_updated': str(datetime.now()),
        'jar_version': new_jar_file_path[-9:-4],
        'jar_hash': str(url_hash)
    }

    set_configs(config, update_config)
    return update_config['jar_version']


def update_kolmafia_jar(config, mafia_folder):
    """ #######################################################################
    Main function to update the Kolmafia JAR file.
    Args:   config (configparser.ConfigParser): Configuration object
            mafia_folder (str): Folder path where the JAR file will be saved
    ####################################################################### """
    config.set('DEFAULT', 'last_run', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("Fetching latest build - this can take a few seconds\n")
    try:  # Retrieve the HTML content
        response = requests.get(KOLMAFIA_BUILD_URL)
        response.raise_for_status()  # Raise an exception for any HTTP error
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    download_url = KOLMAFIA_BUILD_URL + next(link['href'] for link in soup.find_all('a', href=True) if
                                             link['href'].endswith('.jar'))

    if download_url:
        url_hash = hashgen.generate_hash_from_url(download_url)
        config_info = verify_configuration(config, mafia_folder)
        if config_info['jar_file'] is not None:
            if config_info['version'] is None:
                set_configs(config, {'jar_version': config_info['jar_file'][-9:-4]})
            if config_info['hash'] is None:
                local_file = os.path.join(mafia_folder, str(config_info['jar_file']))
                hash_value = hashgen.generate_hashes_from_local_file(local_file)
                set_configs(config, {'jar_hash': str(hash_value)})
            if url_hash != config.get('DEFAULT', 'jar_hash', fallback=''):
                result = "update"
            else:
                result = "up to date"
        else:
            result = "repair"

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

        if result != "up to date":
            jar_version = download_and_update_kolmafia_jar(config, mafia_folder, download_url, url_hash)

        match result:
            case "update":
                print(f"New version of Mafia found, updating to version {jar_version}.")
            case "repair":
                print(f"No JAR files found in the folder - skipping file verification.\n "
                      f"Mafia has been repaired and updated to version {jar_version}.")
            case "up to date":
                print("Mafia is already up to date")


# Main function
def main():
    config = configparser.ConfigParser(defaults=DEFAULT_CONFIG)
    if not os.path.exists(CONFIG_FILE_PATH):  # Check if config.ini exists
        configure.restore_defaults()
        configure.set_destination_folder(config)  # run the script that handles config file setup
    config.read(CONFIG_FILE_PATH)  # Read the configuration from the file
    mafia_folder = config.get('DEFAULT', 'destination_folder', fallback='Not Set')
    update_kolmafia_jar(config, mafia_folder)


if __name__ == "__main__":
    main()
