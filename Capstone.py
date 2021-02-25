from __future__ import print_function
import pickle
import os.path
import requests
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly','https://www.googleapis.com/auth/drive.metadata.readonly']
credentials = service_account.Credentials.from_service_account_file(
        'Capstone-7383c5975015.json', scopes=SCOPES)
delegated_credentials = credentials.with_subject('liam.rowell.17@cnu.edu')

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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
            creds = service_account.Credentials.from_service_account_file(
        'Capstone-7383c5975015.json', scopes=SCOPES)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    #Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId='1zqHDL_biCWzwkFozKYYhoEWc52l1LDD5TpHwG9rlT4g',
                                range='A1:B4').execute()
    values = result.get('values', [])
    
    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[1]))

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(q = "'1XlVByPlwLujL36kwCk4JVpaaP4_QqPvk' in parents",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()