# Google Drive API Task For The Forensics Team

The code in this project is based on Google Drive API. 
The goal is to create a password protected arcvive file and upload it to a google drive, then download the file, extract the content and upload it again. The next stage is getting the logs from the drive and inspect the activity in the drive. 

The key data elemtns that we can find in the logs are:
* When the file was created
* File's metadata (hash, mime type, file name)
* size
* original file name      
* Access by this and other users
    * The name of the last user that accessed the file
    * The last user that modified the file
    * The owner 
    * The user that shared the file with the current user
    * Capabilities of the current user for the file
    * The time in which the file was shared with other users  
* Folders that contain this file    
* Is the file is shareable and it's permissons    
* Is the file editable 

The output of the log is saved in log.json
