from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import secrets

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

INSERT_RANGE = 'DB!A10:N10'
HEX_RANGE 	 = 'DB!N10:N1000'
SEARCH_RANGE = 'DB!A10:N1000' # need to increase if we start getting to 1000
TIME_RANGE 	 = 'DB!B10:B1000'

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
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

def updateVote(time,votes):

	result = sheet.values().get(spreadsheetId=secrets.sheets_id,
								range=TIME_RANGE).execute()
	values = result.get('values', [])

	if not values:
		print('No data found.')
		return True
	else:
		row = 10
		for r in values:
			if r[0] in time:
				break
			elif r[0] == 'end':
				print('build not found for vote')
				return
			row = row + 1
		row = str(row)
		vote_cell = 'DB!I'+row+':I'+row
		print(vote_cell)

		values = [[str(votes)]]
		body = {'values':values}
		print('vote changed!')
		result 	= service.spreadsheets().values().update(
		  spreadsheetId=secrets.sheets_id, range=vote_cell,
		  valueInputOption='USER_ENTERED', body=body,).execute()

def findHex(hexstring):
	result = sheet.values().get(spreadsheetId=secrets.sheets_id,
								range=HEX_RANGE).execute()
	values = result.get('values', [])

	if not values:
		print('No data found.')
		return True
	else:
		row = 10
		for h in values:
			if h and h[0] == hexstring:
				print('Duplicate found')
				return row
			row = row + 1
		
		print('No duplicate found.')
		return False

def findBuild(at,pri,sec,rated):
	result = sheet.values().get(spreadsheetId=secrets.sheets_id,
								range=SEARCH_RANGE).execute()
	values = result.get('values', [])

	emb = {
		'at':'','pri':'','sec':'','build_url':'',
		'author':'','comment_url':'','comment_time':''
	}
	vote = -1

	if not values:
		return False
	else:
		found = False
		for row in values:
			try:
				if at in row[2].lower() and pri in row[3].lower() and sec in row[4].lower():
					if int(row[8]) > vote:
						found = True
						vote = int(row[8])
						emb['author'] 		= row[0]
						emb['comment_time'] = row[1][0:10]
						emb['at'] 			= row[2]
						emb['pri'] 			= row[3]
						emb['sec'] 			= row[4]
						emb['build_url'] 	= row[11]
						emb['comment_url'] 	= row[12]
						if not rated:
							return emb
						elif vote > 0:
							return emb
			except:
				continue
		if found:
			return emb
		else:
			print('No exact match found')
			return False

	return False

def add(entry):
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
			  spreadsheetId=secrets.sheets_id, range=INSERT_RANGE,
			  valueInputOption='USER_ENTERED', body=body,).execute()
