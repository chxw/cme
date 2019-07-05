# cme

Note: `client_secret.json` is given to you by Google APIs in order to create a client to interact with the Google Drive API (with permission to access certain files on Google Drive). I've not pushed this file to the repo...

# crontab
Crontab is used with this `.py` to automate collected updated seat prices at the beginning and end of everyday using this snippet:

If file is in a directory with a venv:
```
SHELL=/bin/bash

MAILTO=""

30 11, 16 * * 1-5 cd /path/to/file_directory && source env/bin/activate && python seatprices.py
```

If file is in a directory without a venv:
```
SHELL=/bin/bash

MAILTO=""

30 11, 16 * * 1-5 python /path/to/file
```
