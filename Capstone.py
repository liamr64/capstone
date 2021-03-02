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
AVAILABLE_ROOM = 'Available Room Data (should include all room types)'
MYSQL_CONFIG = {
  'user': 'admin',
  'password': '1387194#',
  'host': 'database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com',
  'database': 'Capstone',
  'raise_on_warnings': True
}

def main():
    creds = getCreds()

    lotteries = getFiles(MAIN_DIRECTORY, creds)

    if lotteries is None:
        print("There are no lotteries.  Even I'm not that good")
    for lottery in lotteries:
        lotteryInfo = getFiles(lottery['id'],creds)
        uniId =sendLotteryInfo(lotteryInfo, creds)
        sendRoomData(lotteryInfo, uniId,creds)


    


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
    curA = conn.cursor()
    curA.execute(query)
    results = curA.fetchall()
    conn.commit()
    conn.close()
    return results



def sendLotteryInfo(lotteryInfo, creds):
    for doc in lotteryInfo:
        if doc['name'] == LOTTERY_DATA:
            data = getSheets(doc['id'], 'A1:B6', creds)
            tables = 'INSERT INTO Lottery (LotteryName, University,StartTime,timeBetween, numSlots, numTimes) '
            values = 'VALUES ("%s", "%s","%s",%d, "%s", %d) ' % (data[0][1],data[1][1],data[2][1],int(data[3][1]),data[4][1],int(data[5][1]))
            update = 'ON DUPLICATE KEY UPDATE StartTime = "%s",timeBetween = %d, numSlots = %d, numTimes = %d' % (data[2][1],int(data[3][1]),int(data[4][1]),int(data[5][1]))
            query = tables + values + update
            sendQuery(query)
            uniId=sendQuery('SELECT idLottery from Lottery')
            return uniId[0][0]

def sendRoomData(lotteryInfo,uniId,creds):   
    for doc in lotteryInfo:   
        if doc['name'] == AVAILABLE_ROOM:
            data = getSheets(doc['id'], 'A1:E32', creds)
            processRoomData(data,uniId)

def processRoomData(data, uniId):
    data.pop(0)
    for row in data:
        if len(row) != 0 and 'contract' not in row[0]:
            if row[0] != '':
                tables = 'INSERT INTO Residence_Hall (ResName, Lottery_idLottery) '
                values = 'VALUES ("%s", %d) ' % (row[0], uniId)
                update = 'ON DUPLICATE KEY UPDATE ResName = "%s"' % (row[0])
                query = tables + values + update
                print(query)
                sendQuery(query)
                buildingId = sendQuery('SELECT idResidence_Hall from Residence_Hall')
            tables = 'INSERT INTO Room (RoomName, Occupancy,numAvailable, Residence_Hall_idResidence_Hall) '
            values = 'VALUES ("%s", %d,%d,%d) ' % (row[3],int(row[2]),int(row[1]),buildingId[0][0])
            update = 'ON DUPLICATE KEY UPDATE numAvailable = %d' % (int(row[1]))
            query = tables + values + update
            print(query)
            sendQuery(query)
            
                

            
            




if __name__ == '__main__':
    main()