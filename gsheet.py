from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import secrets

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

RANGE_NAME = 'DB!A10:N10'
HEX_RANGE = 'DB!N10:N1000'

def find(hexstring):
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('sheets', 'v4', credentials=creds)
	# Call the Sheets API
	sheet 	= service.spreadsheets()
	result = sheet.values().get(spreadsheetId=secrets.sheets_id,
								range=HEX_RANGE).execute()
	values = result.get('values', [])

	if not values:
		print('No data found.')
		return True
	else:
		for h in values:
			if h and h[0] == hexstring:
				print('Duplicate found')
				return True
		
		print('No duplicate found.')
		return False

def add(entry):

	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('sheets', 'v4', credentials=creds)
	# Call the Sheets API
	sheet 	= service.spreadsheets()

	rowrange = {"sheetId": secrets.sheets_num,"startRowIndex": 9,"endRowIndex": 10,"startColumnIndex": 0,"endColumnIndex": 14}
	requests = []
	requests.append({
		'insertRange': {
			'range': rowrange,
			'shiftDimension': 'ROWS'
		}
	})
	# requests.append({
	# 	'updateCells': {
	# 		'rows': [{'values':}]
	# 	}
	# })

	body = {'requests':requests}

	result 	= service.spreadsheets().batchUpdate(
			  spreadsheetId=secrets.sheets_id, body=body).execute()

	body = {
		'values': entry
	}
	result 	= service.spreadsheets().values().update(
			  spreadsheetId=secrets.sheets_id, range=RANGE_NAME,
			  valueInputOption='USER_ENTERED', body=body,).execute()
