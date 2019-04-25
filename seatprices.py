# Overall this is pretty impressive. You made use of a number of third-party libraries and the authentication piece with 
# G Sheets is not easy! Even though you used a 3rd party SDK, still kudos are in order. 
# I see no major changes needed, though how you design classes can depend heavily on what the rest of the app looks like. 
# Below I put some suggestions in-line, search for XM: to look at my comments :) 


# Import libraries
import time
import datetime
import requests
from bs4 import BeautifulSoup
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

################################################
## Classes 
################################################
class Exchange:
	
	# XM: make these constants ALL CAPS :) https://www.python.org/dev/peps/pep-0008/#constants
	cme_divisions = 4 # cme, imm, iom, gem
	cbot_divisions = 5 # full, am, gim, idem, com
	nymexComex_divisions = 3 # nymex, comex full, comex options

	# XM: consider not getting users to pass in a string, and instead expose a couple of options. 
	# In other words, multiple choice instead of "freeform". One way is to expose a couple of constants (class variables) 
	# CME = "cme"
	# CBOT = "cbot" 
	# NYMEX = "nymexComex" 

	# Then, later, you can do: 
	
	#	if self.name == self.CME: 
	# 		divisions = self.cme_divisions
	#       etc,......
	
	 
	
	def __init__(self, name):
		self.name = name
		self.data = []
	
	
	## XM: Webscraping is generally a pretty messy and brittle operation.  
	## That said, I think you managed to keep it pretty clean. Rule of thumb is to use ID when possible, else use CLASS, else use TYPE for HTML elements. 
	def scrape(self):
		# Collect first membership pricing page
		page = requests.get("https://www.cmegroup.com/company/membership/membership-and-lease-pricing.html#"+self.name)

		# Create a BeautifulSoup object
		soup = BeautifulSoup(page.text, 'html.parser')

		# Locate table cells where seat prices are
		table_cells = soup.find(class_=self.name+" parsys")
		seat_prices = table_cells.find_all(lambda tag:tag.name=="td" and "$" in tag.get_text())
		
		
		# Which exchange?
		if self.name == "cme":
			divisions = self.cme_divisions
		elif self.name == "cbot":
			divisions = self.cbot_divisions
		elif self.name == "nymexComex":
			divisions = self.nymexComex_divisions
				
		
		
		

		# Truncate - index list to remove anything past seat prices table + remove 3rd col: "Last Sale"
		i = 1
		for table_cells in seat_prices[0:divisions*3]:
			if i % 3 != 0:
				self.data.append(table_cells.contents[0])
			i += 1

		# Remove symbols '$,*'
		# XM: good comment. 
		self.data = [re.sub("[$,*]", "", x) for x in self.data]

		# Convert str to int
		self.data = [int(x) for x in self.data]

################################################
## Functions
################################################
def insert_to_gsheets(*args):
	# Join lists of data together
	row = []
	for data in args:
		row = row+data

	# Finish row by adding timestamp
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	row.insert(0, st)

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
	
	
	## XM: nice, but you can simplify by inserting the values to the last row: 
	# https://gspread.readthedocs.io/en/latest/api.html?highlight=append#gspread.models.Spreadsheet.values_append

################################################
## Main
################################################
def main():
	
	# XM: very elegant OOP design! 
	CME = Exchange(name="cme")
	CME.scrape()

	CBOT = Exchange(name="cbot")
	CBOT.scrape()

	NC = Exchange(name="nymexComex")
	NC.scrape()

	# Insert data to gsheets
	insert_to_gsheets(CME.data, CBOT.data, NC.data)

main()
