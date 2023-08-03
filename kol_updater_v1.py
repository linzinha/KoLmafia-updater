import configparser
import hashlib
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup


# Constants
username = os.getlogin()
starting_path = os.path.join('C:\\Users', username)
url = 'https://ci.kolmafia.us/job/Kolmafia/lastSuccessfulBuild/'
config_file_path = "config.ini"
YES_OPTIONS = {'y', 'yes'}
NO_OPTIONS = {'n', 'no'}
CANCEL_OPTIONS = {'c', 'cancel'}

# Check if config.ini exists, if not, create it with the default path
if not os.path.exists(config_file_path):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'destination_folder': starting_path,
                         'current_hash': '1f87eb9b2e347d3d40b1ff004f0dc367ed8f994c3d37fa8d7d1e68b160692d8e',
                         'last_run': 'None',
                         'status': 'False',
                         'schedule_type': 'None',
                         'schedule_interval': 'None',
                         'notifications': 'False',
                         'backup': 'False',
                         'confirmation': 'False',
                         'startup_trigger': 'False',
                         'time_trigger': 'False',
                         'interval_trigger': 'False'
                         }
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

# Load the stored folder at the beginning
config = configparser.ConfigParser()
config.read(config_file_path)
stored_folder = config['DEFAULT']['destination_folder'].strip()


def set_destination_folder():
    global stored_folder
    folder = input(f"\nEnter the destination folder path\n"
                   f"----------\n"
                   f"- Start the line with a backslash to traverse out of the current directory\n"
                   f"- Enter c to [c]ancel\n"
                   f"----------\n"
                   f"Destination Folder Path: {stored_folder}\\")
    if folder.lower() in CANCEL_OPTIONS:
        return stored_folder
    else:
        folder = os.path.join(stored_folder, folder)
        verify = input(f"\nYou entered {folder}, is this correct? ([y]es/[n]o/[c]ancel): ")
        if verify.lower() in YES_OPTIONS:
            if not os.path.exists(folder):
                print("Error: The folder does not exist. Is this correct?")
                return stored_folder

            with open(config_file_path, "w") as config_file:
                config = configparser.ConfigParser()
                config['DEFAULT'] = {'destination_folder': folder}
                config.write(config_file)

            # Update the stored_folder variable with the new value
            stored_folder = folder
            print("Destination folder has been set successfully.\n")
            return folder
        elif verify in NO_OPTIONS:
            return set_destination_folder()
        elif verify in CANCEL_OPTIONS:
            return stored_folder
        else:
            print("Invalid choice. Please try again.")
            return set_destination_folder()


def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def run_updater():
    # Get the current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("Fetching latest build - this can take a few seconds\n")
    result = None

    with open(config_file_path, "r") as config_file:
        folder = config_file.read().strip()
        if not folder:
            print("Error: Destination folder is not set.")
            return

        # Extract the current jar file version
        current_file = next((file for file in os.listdir(stored_folder) if file.endswith('.jar')), "")

        # Retrieve the HTML content
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for any HTTP error
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            exit(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        new_jar_link = next(link['href'] for link in soup.find_all('a', href=True) if
                            link['href'].endswith('.jar'))

        if new_jar_link:
            new_file = os.path.join(stored_folder, os.path.basename(new_jar_link))
            new_file_name = str(new_file.split("\\")[-1:])[2:-2]
            try:
                response = requests.get(url + new_jar_link, stream=True)
                response.raise_for_status()  # Raise an exception for any HTTP error
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                exit(1)
            with open(new_file, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

            # Get the current jar file path and hash from the config file
            config = configparser.ConfigParser()
            config.read(config_file_path)
            current_hash = config.get('DEFAULT', 'current_hash', fallback=None)
            current_file_path = os.path.join(stored_folder, current_file)

            # If current hash is not present, calculate the hash and update the config file
            if not current_hash and os.path.exists(current_file_path):
                current_hash = calculate_hash(current_file_path)
                config.set('DEFAULT', 'current_hash', current_hash)
                with open(config_file_path, "w") as config_file:
                    config.write(config_file)

            # Calculate the hash of the downloaded file
            new_hash = calculate_hash(new_file)
            print(f"Downloaded File: {new_hash}")
            print(f"Current file: {current_hash}")

            # Compare the hashes
            if current_hash and current_hash == new_hash and current_file:
                current_file_status = "Mafia is up to date: "
                result = "The downloaded file's hash matches the current file. Download removed."
                os.remove(new_file)  # Remove the newly downloaded file as it is identical to the current one
            else:
                # Update the current jar file hash in the config file
                config.set('DEFAULT', 'current_hash', new_hash)
                with open(config_file_path, "w") as config_file:
                    config.write(config_file)

                if current_file:
                    try:
                        current_file_status = f"{current_file} removed"
                        os.remove(current_file)

                    except OSError as e:
                        result = f"Error: {e}"
                if not current_file:
                    current_file_status = "Jar file was missing, Mafia has been repaired."
                result = f"File '{new_file_name}' has been moved to '{current_file_path}'. " \
                         f"Mafia updated to version {new_file[-9:-4]}."

        # Update the last_run field in the config file with the current date and time
        config.set('DEFAULT', 'last_run', current_datetime)
        with open(config_file_path, "w") as config_file:
            config.write(config_file)

        print(f"\n{current_file_status}\n"
              f"{result}")


def main():
    global stored_folder
    while True:
        print("\nMenu:")
        print(f"1. Set destination folder [CURRENTLY {stored_folder}]")
        print("2. Run updater")
        print("3. Set updater to run automatically [IN DEVELOPMENT]")
        print("0. Exit\n")

        choice = input("Enter your choice: ")

        if choice == "1":
            stored_folder = set_destination_folder()
        elif choice == "2":
            run_updater()
        elif choice == "3":
            print("Feature in development")
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
