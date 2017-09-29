import requests, re, gspread, os
from bs4 import BeautifulSoup
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials as SAC

# Basic Setup
LOC_DIR = os.path.dirname(os.path.realpath(__file__))
OPEN_DATA_API_KEY = os.environ.get("VELIB_WEBHOOK_SECRET")
GOOGLE_DRIVE_API_KEY = os.environ.get("GOOGLE_DRIVE_SECRET")
VELIB_SPREADSHEET_CREDENTIAL = os.environ.get("VELIB_SPREADSHEET_SECRET")
CITY="Marseille"
'''
Cité 			|	Nom
----------------------------------
Amiens			|	Velam
Besancon		|	VéloCité
Cergy-Pontoise	|	Velo2
Creteil 		|	Cristolib
Lyon			|	Vélo'V
Marseille		|	Le vélo
Mulhouse		|	VéloCité
Nancy			|	vélOstan'lib
Nantes			|	Bicloo
Paris			|	Velib
Rouen			|	cy'clic
Toulouse		|	Vélô
'''
OUTPUT_DIR = os.path.join(LOC_DIR, 'Output/{}.csv').format(CITY)
OPEN_DATA_URL = "https://api.jcdecaux.com/vls/v1/stations?contract={0}&apiKey={1}".format(CITY, OPEN_DATA_API_KEY)

def grabData(OPEN_DATA_URL=OPEN_DATA_URL):
	response = requests.get(OPEN_DATA_URL).json()
	return response

def get_station_data(response, flag="static"):
	station_data_list = list()
	index_list = list()
	if flag is "static":
		for data in response:
			data_json ={
				# static data
				"name" : data['name'],
				"bike_stands" : data['bike_stands'],
				"address" : data['address'],
				"lat" : data['position']['lat'],
				"lng" : data['position']['lng'],
				# dynamic data
				"status" : data['status'], 
				"last_update" : datetime.fromtimestamp(int(str(data['last_update'])[:10])).strftime('%Y-%m-%d %H:%M:%S')
				}
			station_data_list.append(data_json)
	elif flag is "dynamic":
		for data in response:
			data_json ={
				# static data
				"name" : data['name'],
				"bike_stands" : data['bike_stands'],
				"address" : data['address'],
				"lat" : data['position']['lat'],
				"lng" : data['position']['lng'],
				# dynamic data
				"available_bikes" : data['available_bikes'], 
				"available_bike_stands" : data['available_bike_stands'], 
				"status" : data['status'], 
				"last_update" : datetime.fromtimestamp(int(str(data['last_update'])[:10])).strftime('%Y-%m-%d %H:%M:%S')
				}
			station_data_list.append(data_json)
	return station_data_list


def exchange_data_with_gspread(GOOGLE_DRIVE_API_KEY, VELIB_SPREADSHEET_CREDENTIAL, DATA):
	try:
		scope = ['https://spreadsheets.google.com/feeds']
		credential = SAC.from_json_keyfile_name(GOOGLE_DRIVE_API_KEY, scope)

		sp = gspread.authorize(credential)
		# Data Sheet is located at sheet1
		# Check Google Drive
		sp = sp.open_by_key(VELIB_SPREADSHEET_CREDENTIAL)
		sp = sp.sheet1

	except Exception as e:
		print("Connection with Google Spread Sheet: Velib is failed.")
		print(e)

def export_to_csvfile(DATA):
	try:
		import pandas as pd
		df = pd.DataFrame(DATA)
		df.to_csv(OUTPUT_DIR, index=False)
		print("Write CSV file successfully!")
	except Exception as e:
		print(e)

def main():
	global response, station_data
	response = grabData()
	station_data = get_station_data(response)
	export_to_csvfile(station_data)

if __name__ == '__main__':
	main()
