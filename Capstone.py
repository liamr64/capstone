from __future__ import print_function
import pickle
import os.path
import mysql.connector
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
MAIN_DIRECTORY = '1XlVByPlwLujL36kwCk4JVpaaP4_QqPvk'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'
LOTTERY_DATA = 'Lottery Data'
MYSQL_CONFIG = {
  'user': 'admin',
  'password': '1387194#',
  'host': 'database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com',
  'database': 'Capstone',
  'raise_on_warnings': True
}

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = getCreds()

    lotteries = getFiles(MAIN_DIRECTORY, creds)

    if lotteries is None:
        print('fuckity fuck fuck fuck no lotteries found thats an issue')
    for lottery in lotteries:
        print(lottery['name'])
        lotteryInfo = getFiles(lottery['id'],creds)
        sendInfo(lotteryInfo, creds)

    


def getCreds():
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
    
    return creds

def getFiles(parentFile, creds):
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(q ="'"+ parentFile + "'" + " in parents",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    return items

def getSheets(sheetId,range, creds):
    service = build('sheets', 'v4', credentials=creds)

    #Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheetId,
                                range=range).execute()
    values = result.get('values', [])
    return values

def sendQuery(query):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    curA = conn.cursor(buffered=True)
    curA.execute(query)
    conn.commit()
    conn.close()



def sendInfo(lotteryInfo, creds):
    for doc in lotteryInfo:
        if doc['name'] == LOTTERY_DATA:
            data = getSheets(doc['id'], 'A1:B6', creds)
            tables = 'INSERT INTO Lottery (LotteryName, University,StartTime,timeBetween, numSlots, numTimes) '
            values = 'VALUES ("%s", "%s","%s",%d, "%s", %d)' % (data[0][1],data[1][1],data[2][1],int(data[3][1]),data[4][1],int(data[5][1]))
            query = tables + values
            print(query)
            sendQuery(query)



if __name__ == '__main__':
    main()