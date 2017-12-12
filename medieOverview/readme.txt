Movie clip organizer

This project is only tested on python2 and windows.

To get started:
 1. run setup.bat - that will install django python package, set up db, and create superuser account
 2. run start-server.bat and open webpage http://127.0.0.1:9888 and log in with user from step 1
 3. Go to admin and add a new Movie folder
 4. Run start-worker.bat
 5. Go back to main page and click on "Folders" in top menu
 6. Click "scan" on the folder you added
 7. Wait while worker goes through and indexes the film clips
 8. (Optional but recommended) Install VLC protocol hook from https://github.com/stefansundin/vlc-protocol
 9. Enjoy