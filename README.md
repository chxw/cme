# Getting Started
1. Git clone/download `cme`
2. Within `cme` folder, start up a virtual environment: `python3 -m venv /path/to/venv/`
3. Activate venv: `source venv/bin/activate`
4. Run script: `python3 seatprices.py`

# Notes
## gspread

Note: `client_secret.json` is given to you by Google APIs in order to create a client to interact with the Google Drive API (with permission to access certain files on Google Drive). I've not pushed this file to the repo...

## crontab
Crontab is used with this script to automate collected updated seat prices at the beginning and end of everyday using this snippet:

Using `venv` example:
```
SHELL=/bin/bash

MAILTO=""

30 11,16 * * 1-5 cd /path/to/file_directory && source env/bin/activate && python seatprices.py
```

Not using `venv` example:
```
SHELL=/bin/bash

MAILTO=""

30 11,16 * * 1-5 cd /path/to/python /path/to/file_directory/seatprices.py 
```
