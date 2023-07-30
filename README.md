# KoLmafia-updater

## Setting the destination folder
When you first run the script, you will need to point it to Mafia's location with option 1 on the main menu. The default path is your user's home folder, and all entries will be RELATIVE paths to that home folder, like so:

```
Menu:
1. Set destination folder [CURRENTLY C:\Users\Linzinha]
2. Run updater
3. Set updater to run automatically [IN DEVELOPMENT]
0. Exit

Enter the destination folder path
----------
- Start the line with a backslash to traverse out of the current directory
- Enter c to [c]ancel
----------
Destination Folder Path: C:\Users\Linzinha\Documents\KoLmafia

You entered C:\Users\Linzinha\Documents\KoLmafia, is this correct? ([y]es/[n]o/[c]ancel): y
Destination folder has been set successfully.
```

[y]es will save the file
[n]o will reprompt for user input
[c]ancel will keep the previoussly defined destination folder set and return to the main menu

This information is stored in the `config.ini` file and can also be changed manually

## Run the updater manually
The script will then do the following steps:
- find and download the current .jar file on `https://ci.kolmafia.us/job/Kolmafia/lastSuccessfulBuild/`
- it will then check the hash value of the new and existing .jar files
 - if the hashes are identical iy will delete the new download
 - if they aren't identical, the new download replaces to .jar file in the destination folder and the Mafia is now updated!

```
Menu:
1. Set destination folder [CURRENTLY C:\Users\Linzinha\Documents\KoLmafia]
2. Run updater
3. Set updater to run automatically [IN DEVELOPMENT]
0. Exit

Enter your choice: 2
Downloaded File: c80e6586e6ef422585e8014e6488d6d699f00325c8ab325414d18719c8340e67
Current file: 1be2156552cc2a934ce4f5c7347f5d6fc4bbe51e0776d8c4acc6014f54e73951

KoLmafia-27498.jar removed
File 'KoLmafia-27498.jar' has been moved to ''C:\Users\Linzinha\Documents\KoLmafia\'. Mafia updated to version 27499.
```

```
Enter your choice: 2
Fetching latest build - this can take a few seconds

Downloaded File: 7c50da4d34cbe04c3cd11079253c14403b56f586a82f93fbd54df88311e3de71
Current file: 7c50da4d34cbe04c3cd11079253c14403b56f586a82f93fbd54df88311e3de71

Jar file was missing, Mafia has been repaired.
File 'KoLmafia-27501.jar' has been moved to 'C:\Users\Linzinha\Documents\KoLmafia\'. Mafia updated to version 27501.

Menu:
1. Set destination folder [CURRENTLY C:\Users\Linzinha\Documents\KoLmafia]
2. Run updater
3. Set updater to run automatically [IN DEVELOPMENT]
0. Exit

Enter your choice: 0

Process finished with exit code 0
```

## Requirements
requests~=2.31.0
beautifulsoup4~=4.12.2

