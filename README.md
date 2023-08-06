# KoLmafia-updater

## Requirements
- requests~=2.31.0
- beautifulsoup4~=4.12.2

### Python version
Due to the use of switch case handling, this script **requires** at least Python 3.10 or later.

It was written with version 3.11.3

### OS
While the goal is to be OS Agnostic, I've only tested so far on Windows 10 so cannot confirm full compatibility with Linux/Unix systems. Testing is appreciated!


## Setting the destination folder
When you first run the script, you will need to point it to Mafia's location with option 1 on the main menu. The default path is your user's home folder, and all entries will be RELATIVE paths to that home folder, like so:

```
Menu:
1. Set destination folder [CURRENTLY C:\Users\Linzinha]
2. Run updater
3. Configure automatic updater [IN DEVELOPMENT]
0. Exit

Enter the destination folder path (or c to [c]ancel)
--------------
Current Destination Folder Path: C:\Users\Linzinha\
--------------
Set New Destination Folder Path: C:\Users\Linzinha\Documents\KoLmafia

You entered C:\Users\Linzinha\Documents\KoLmafia, is this correct? ([y]es/[n]o/[c]ancel): y
Destination folder has been set successfully.
```

- [y]es will save the file
- [n]o will reprompt for user input
- [c]ancel will keep the previoussly defined destination folder set and return to the main menu

This information is stored in the `config.ini` file and can also be changed manually

## Running kol_updater manually
When selecting option 2, The script will then do the following steps:
1. find and download the current .jar file on `https://ci.kolmafia.us/job/Kolmafia/lastSuccessfulBuild/`
2. check the hash value of the new .jar file and the hash saved in the config file
3. if no hash exists in the config file, the script falls back to checking the existing .jar file
4. if the hashes are identical it will delete the new download
5. if they aren't identical, the new download replaces to .jar file in the destination folder and the Mafia is now updated!

## Using quickupdate

If you've successfully run any version of kol_updater, just make sure that the `quickupdate.exe` or `quickupdate.py` file is in the exact same folder as your `config.ini` file and it should work just fine. Otherwise, it will run with the default configuration

If you are running it without running `kol_updater`.py or .exe,just make sure to write a config file with the following information:

```
[DEFAULT]
destination_folder = YOUR_DESTINATION_FOLDER
last_run = 
last_updated = 
jar_version = 
jar_hash = 
```
