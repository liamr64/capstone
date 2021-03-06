from __future__ import print_function
import pickle
import os.path
from datetime import datetime
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient import discovery


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
        '/var/www/html/Capstone-7383c5975015.json', scopes=SCOPES)
delegated_credentials = credentials.with_subject('liam.rowell.17@cnu.edu')

# The ID and range of a sample spreadsheet.
MAIN_DIRECTORY = '1XlVByPlwLujL36kwCk4JVpaaP4_QqPvk'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'
LOTTERY_DATA = 'Lottery Data'
AVAILABLE_ROOM = 'Available Room Data (should include all room types)'
UPDATE_TIMES = 'Update Times'
MYSQL_CONFIG = {
  'user': 'admin',
  'password': '1387194#',
  'host': 'database-1.cnth4dgmksji.us-east-2.rds.amazonaws.com',
  'database': 'Capstone',
  'raise_on_warnings': True
}

import mysql.connector
if mysql.connector.__version_info__ > (2, 1) and mysql.connector.HAVE_CEXT:
  MYSQL_CONFIG['use_pure'] = False


def main():
    creds = getCreds()

    lotteries = getFiles(MAIN_DIRECTORY, creds)
    
    if lotteries is None:
        print("There are no lotteries.  Even I'm not that good")
    for lottery in lotteries:
        lotteryInfo = getFiles(lottery['id'],creds)
        updateId = showUpdate(lotteryInfo, creds)
        uniId =sendLotteryInfo(lotteryInfo,updateId, creds)
        sendRoomData(lotteryInfo, uniId,creds)
        sendSimData(lotteryInfo,uniId, creds)
        showUpdate(lotteryInfo, creds)



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
        '/var/www/html/Capstone-7383c5975015.json', scopes=SCOPES)
        # Save the credentials for the next run
        with open('/var/www/html/token.pickle', 'wb') as token:
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

def sendQuery(query, insert):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    curA = conn.cursor()
    curA.execute(query)
    if not insert:
        results = curA.fetchall()
        conn.commit()
        conn.close()
        return results
    else:
        conn.commit()
        conn.close()



def sendLotteryInfo(lotteryInfo, updateId, creds):
    for doc in lotteryInfo:
        if doc['name'] == LOTTERY_DATA:
            data = getSheets(doc['id'], 'A1:B6', creds)
            tables = 'INSERT INTO Lottery (LotteryName, University,StartTime,timeBetween, numSlots, numTimes, updateTableid) '
            values = 'VALUES ("%s", "%s","%s",%d, "%s", %d, "%s") ' % (data[0][1],data[1][1],data[2][1],int(data[3][1]),data[4][1],int(data[5][1]), updateId)
            update = 'ON DUPLICATE KEY UPDATE StartTime = "%s",timeBetween = %d, numSlots = %d, numTimes = %d, updateTableid = "%s";' % (data[2][1],int(data[3][1]),int(data[4][1]),int(data[5][1]),updateId)
            query = tables + values + update
            sendQuery(query, True)
            getId = 'SELECT idLottery from Lottery where LotteryName = "%s";' % (data[0][1])
            uniId=sendQuery(getId, False)
            return uniId[0][0]

def sendRoomData(lotteryInfo,uniId,creds): 
    for doc in lotteryInfo:   
        if doc['name'] == AVAILABLE_ROOM:
            data = getSheets(doc['id'], 'A1:E32', creds)
            processRoomData(data,uniId)
            break

def processRoomData(data, uniId):
    data.pop(0)
    for row in data:
        if len(row) != 0 and 'contract' not in row[0]:
            if row[0] != '':
                tables = 'INSERT INTO Residence_Hall (ResName, Lottery_idLottery) '
                values = 'VALUES ("%s", %d) ' % (row[0], uniId)
                update = 'ON DUPLICATE KEY UPDATE ResName = "%s";' % (row[0])
                query = tables + values + update
                sendQuery(query, True)
                findBuilding = 'SELECT idResidence_Hall from Residence_Hall where ResName = "%s" and Lottery_idLottery = %d;' % (row[0], uniId)
                buildingId = sendQuery(findBuilding, False)
            tables = 'INSERT INTO Room (RoomName, Occupancy,numAvailable, Residence_Hall_idResidence_Hall) '
            values = 'VALUES ("%s", %d,%d,%d) ' % (row[3],int(row[2]),int(row[1]),buildingId[0][0])
            update = 'ON DUPLICATE KEY UPDATE numAvailable = %d;' % (int(row[1]))
            query = tables + values + update
            sendQuery(query, True)


                
def sendSimData(lotteryInfo, uniId, creds):
    simDataPresent = False
    for doc in lotteryInfo:
        if doc['name'] == 'Faked Data':
            files = getFiles(doc['id'], creds)
            simDataPresent = True
            break
    if  not simDataPresent:
        return
    for year in files:
        data = getSheets(year['id'],'A2:F98',creds)
        roomIdsQuery = 'SELECT Room.RoomName, Residence_Hall.ResName, Room.id from Room inner join Residence_Hall on Room.Residence_Hall_idResidence_Hall = idResidence_Hall where Lottery_idLottery = %d;' %(uniId)
        roomIds = sendQuery(roomIdsQuery, False)
        roomDict = createRoomDict(roomIds)
        processSimData(data, year['name'], roomDict)

def createRoomDict(roomIds):
    roomDict = {}
    for roomId in roomIds:
        roomDict['%s, %s' % (roomId[1], roomId[0])] = roomId[2]
    return roomDict


def processSimData(data, year, roomDict):
    ts = time.time()
    timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    i = 0
    while i<len(data):
        j = 1
        while j<len(data[i]):
            if len(data[i][j])>0:
                tables = 'INSERT INTO SampleData (Room_id, Year,Time, Slot, updateTime) '
                values = 'VALUES (%d, %d, "%s", %d, "%s") ' % (int(roomDict[data[i][j]]), int(year), data[i][0], j, timestamp)
                update = 'ON DUPLICATE KEY UPDATE updateTime = "%s";' % (timestamp)
                query = tables + values + update
                sendQuery(query, True)
            j= j +1
            
        i=i+1

def showUpdate(lotteryInfo, creds):
    for doc in lotteryInfo:
        if doc['name'] == UPDATE_TIMES:
            service = discovery.build('sheets', 'v4', credentials=creds)
            range_ = 'B1'
            value_input_option = 'RAW'
            now = datetime.now()
            array = [now.strftime("%m/%d/%Y %H:%M:%S")]
            value_range_body = {"range": "B1", "values": [array]}
            request = service.spreadsheets().values().update(spreadsheetId=doc['id'], range=range_, valueInputOption=value_input_option, body=value_range_body)
            response = request.execute()
            return doc['id']


if __name__ == '__main__':
    main()