import os
import requests
from bs4 import BeautifulSoup

# Get the current username
username = os.getlogin()

# Specify the URL and destination folder path
url = 'https://ci.kolmafia.us/job/Kolmafia/lastSuccessfulBuild/'
destination_folder = os.path.join('C:\\Users', username, 'Documents', 'KoLmafia')

# Extract the current jar file version
current_file = next((file for file in os.listdir(destination_folder) if file.endswith('.jar')), "")

# Retrieve the HTML content
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for any HTTP error
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# Find the download link for the new jar file
new_jar_link = next((link['href'] for link in soup.find_all('a', href=True) if link['href'].endswith('.jar') and link['href'][-9:] != current_file[-9:]), None)

if new_jar_link:
    new_file = os.path.join(destination_folder, os.path.basename(new_jar_link))
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

    if current_file:
        try:
            os.remove(os.path.join(destination_folder, current_file))
        except OSError as e:
            print(f"Error: {e}")
        else:
            print(f"Old file '{current_file}' removed.")

else:
    print("The file ends match. No need to download a new file.")
