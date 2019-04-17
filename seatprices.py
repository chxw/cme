# Import libraries
import time
import datetime
import requests
from bs4 import BeautifulSoup
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

######################################################################
# Functions
######################################################################

# Insert row to correct Google Sheets Drive
def insert_to_gsheets(row):
	# Use creds to create a client to interact with the Google Drive API
	scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	client = gspread.authorize(creds)

	# Open sheet
	sheet = client.open("CME Seat Prices").sheet1

	# Find next available (empty) row
	str_list = list(filter(None, sheet.col_values(1)))
	index = len(str_list)+1

	# Insert our row into Google Sheets doc
	sheet.insert_row(row, index)

######################################################################
# Classes
######################################################################
class Exchange:
	cme_divisions = 4 # cme, imm, iom, gem
	cbot_divisions = 5 # full, am, gim, idem, com
	nymexComex_divisions = 3 # nymex, comex full, comex options

	def __init__(self, name):
		self.name = name

	def retrieve(self):
		# Collect first membership pricing page
		page = requests.get("https://www.cmegroup.com/company/membership/membership-and-lease-pricing.html#"+self.name)

		# Create a BeautifulSoup object
		soup = BeautifulSoup(page.text, 'html.parser')

		# Locate table cells where seat prices are
		table_cells = soup.find(class_=self.name+" parsys")
		seat_prices = table_cells.find_all(lambda tag:tag.name=="td" and "$" in tag.get_text())

		return seat_prices

	def clean(self, collected):
		# Which exchange?
		if self.name == "cme":
			divisions = self.cme_divisions
		elif self.name == "cbot":
			divisions = self.cbot_divisions
		elif self.name == "nymexComex":
			divisions = self.nymexComex_divisions

		### Truncate
		# 1. Get desired seat prices from HTML table cells and put inside prices_list
		# 2. Index list to remove anything past seat prices table
		# 3. Remove 3rd col: "Last Sale"
		prices_list = []
		i = 1
		for table_cells in collected[0:divisions*3]:
			if i % 3 != 0:
				prices_list.append(table_cells.contents[0])
			i += 1

		# Remove symbols '$,*'
		prices_list = [re.sub("[$,*]", "", x) for x in prices_list]

		# Convert str to int
		prices_list = [int(x) for x in prices_list]

		return prices_list

######################################################################
# Main
######################################################################

CME = Exchange(name="cme")
CME_collected = CME.retrieve()
CME_prices = CME.clean(CME_collected)

CBOT = Exchange(name="cbot")
CBOT_collected = CBOT.retrieve()
CBOT_prices = CBOT.clean(CBOT_collected)

nymexComex = Exchange(name="nymexComex")
NC_collected = nymexComex.retrieve()
nymexComex_prices = nymexComex.clean(NC_collected)

# Create row to insert in google sheets
row_to_insert = CME_prices+CBOT_prices+nymexComex_prices

# Finish row_to_insert by adding timestamp
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
row_to_insert.insert(0, st)

# Insert row_to_insert to gsheet
insert_to_gsheets(row_to_insert)
