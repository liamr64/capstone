#   This code is for the actual model itself, as opposed to the other python program, which is
#   the polar

MYSQL_CONFIG = {
  'user': 'admin',
  'password': '1387194#',
  'host': 'database-1.cnth4dgmksji.us-east-2.rds.amazonaws.com',
  'database': 'Capstone',
  'raise_on_warnings': True
}

#constant determining the number of times the polar runs
NUMBER_OF_REPS = 1000



import mysql.connector
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
from scipy.stats import hypergeom
import random
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient import discovery

SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
        'Capstone-7383c5975015.json', scopes=SCOPES)
delegated_credentials = credentials.with_subject('liam.rowell.17@cnu.edu')

#Sends query to the database
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


#main model method
def main():
    lotteries = getLotteries()
    for lottery in lotteries:
        probs = getProbs(lottery)
        if len(probs) != 0: 
            finalprobs = getOverallProbs(probs)
            numSlots = sendQuery('SELECT numSlots FROM Lottery WHERE idLottery = %d;' % (lottery), False)[0][0]
            results = doModel(finalprobs, numSlots, lottery)
            processAndSend(results, lottery, numSlots)
            updateSheets(lottery)
 
 #updates sheets
def updateSheets(lottery):
    updateId = sendQuery('SELECT updateTableid FROM Lottery WHERE idLottery = %d;' % (lottery), False)[0][0]
    creds = getCreds()
    service = discovery.build('sheets', 'v4', credentials=creds)
    range_ = 'B2'
    value_input_option = 'RAW'
    now = datetime.now()
    array = [now.strftime("%m/%d/%Y %H:%M:%S")]
    value_range_body = {"range": "B2", "values": [array]}
    request = service.spreadsheets().values().update(spreadsheetId=updateId, range=range_, valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

#returns the total number of lotteries in the database
def getLotteries():
    lotteries = []
    query = 'SELECT idLottery FROM Lottery;'
    temp = sendQuery(query, False)
    for lottery in temp:
        lotteries.append(lottery[0])

    return lotteries

#calculates and returns probablity of a student choosing a specific room type over the last five years
def getProbs(lottery):
    currentYear = datetime.now().year
    dataYear = currentYear - 1
    data = ['dummy']
    probs = []

    while dataYear >= currentYear - 6 and len(data)>0:
        query = 'SELECT Room_id, SampleData.Time, SampleData.Slot from SampleData INNER JOIN Room on SampleData.Room_id = Room.id INNER JOIN Residence_Hall on Room.Residence_Hall_idResidence_Hall = idResidence_Hall where Lottery_idLottery = %d and SampleData.Year = %d and Residence_Hall_idResidence_Hall = idResidence_Hall;' % (lottery, dataYear) 
        data = sendQuery(query,False)
        if len(data) > 0:
            probs.append(processYear(data))
        dataYear = dataYear -1

    return probs

# helper method for getProbs(), turns raw data from database into probabilities
def processYear(data):
    totalNumber = {}
    numberInFirst = {}
    probablity = {}
    total = 0

    data = sorted(data, key= itemgetter(1,2))

    for record in data:
        roomId = record[0]
        if roomId in totalNumber:
            if totalNumber == 0:
                break
            totalNumber[roomId] = totalNumber[roomId] - 1
            numberInFirst[roomId] = numberInFirst[roomId] + 1
            total = total + 1
        else:
            query = 'SELECT COUNT(Room_id) from SampleData where Room_id = %d;' % (int(roomId))
            count =sendQuery(query, False)
            totalNumber[roomId] = count[0][0]
            numberInFirst[roomId] = 1
            total = total + 1
    
    for roomId in numberInFirst:
        probablity[roomId] = numberInFirst[roomId]/total
    return probablity

#Creates a weighted average of up to five years of specific room probabilites (this is what gets used in the actual model)
def getOverallProbs(listProbs):
    if len(listProbs) == 1:
        return listProbs[0]
    elif len(listProbs) == 2:
        return (.75 * listProbs[0]) + (.5 * listProbs[1])
    elif len(listProbs) == 3:
        return (.66 * listProbs[0]) + (.34 * listProbs[1]) + (.33 * listProbs[2])
    elif len(listProbs) == 4:
        return (.5 * listProbs[0]) + (.17 * listProbs[1]) + (.16 * listProbs[2]) + (.16 * listProbs[3])
    elif len(listProbs) == 5:
        return (.5 * listProbs[0]) + (.125 * listProbs[1]) + (.125 * listProbs[2]) + (.125 * listProbs[3])+ (.125 * listProbs[4])

#Onece specific room probablities have been created, this is where the Monte Carlo happens
def doModel(probs, numSlots, lottery):
    numAvailable = getTotalAvailableRooms(lottery)
    modelRuns = []
    for i in range(0,NUMBER_OF_REPS):
        tempProbs = dict(probs)
        tempNumAvailable = dict(numAvailable)
        modelRuns.append(modelRun(tempProbs, tempNumAvailable, numSlots))
    return modelRuns
        
#Individual run of the Monte Carlo Model, basically one simulated housing lottery
def modelRun(probs, numAvailable, numSlots):
    dist = hypergeom(1000, 24, 1)
    available = []
    anotherRow = True
    i = 0
    while anotherRow:
        availableRow = []
        for j in range(0,numSlots):
            hvar = dist.pmf(i)
            rand1 = random.uniform(0,1)
            availableRow.append(getCurrentAvailability(numAvailable))
            if rand1 >= hvar and anotherRow:
                room = roomPicker(probs)
                numAvailable[room] = numAvailable[room] -1
                if numAvailable[room] == 0:
                    probs, anotherRow = adjustProbs(probs, room)

        available.append(availableRow)     
        i = i+1     
    
    zeroProb = {}
    for key, value in numAvailable.items():
        if value != 0:
            zeroProb[key] = value
    if len(zeroProb) > 0:
        newProb = {}
        for key, value in zeroProb.items():
            newProb[key] = 1/len(zeroProb)
        anotherRow = True
        count = 0
        while anotherRow:
            for j in range(0,numSlots):
                hvar = dist.pmf(i)
                rand1 = random.uniform(0,1)
                availableRow.append(getCurrentAvailability(numAvailable))
                if rand1 >= hvar and anotherRow:
                    room = roomPicker(newProb)
                    numAvailable[room] = numAvailable[room] -1
                    if numAvailable[room] == 0:
                        newProb, anotherRow = adjustProbs(newProb, room)
            available.append(availableRow)
            count = count +1
    
    return available   

#When all rooms of a type have been selected, this resets the probablities to not include a room type
#As a side note, this assumes that the probabilties are independent
def adjustProbs(probs, room):
    newTotal = 1 - probs[room]
    if newTotal < 1e-5:
        return None, False
    probs[room] = 0
    for key, value in probs.items():
        probs[key] = value/newTotal
    return probs, True

def roomPicker(probs):
    rand = random.uniform(0,1)
    rand = float(rand)
    total = 0
    for key, value in probs.items():
        if total + value > rand:
            return key
        else:
            total = total + value

def getCurrentAvailability(numAvailable):
    if numAvailable is None:
        return None
    available = {}
    for key, value in numAvailable.items():
        if value != 0:
            available[key] = True
        else:
            available[key] = False
    return available

def checkIfDone(probs):
    for key, value in probs.items():
        if value != 0:
            return True
    return False

def getTotalAvailableRooms(lottery):
    numAvailable = {}
    results = sendQuery('SELECT id, numAvailable FROM Room INNER JOIN Residence_Hall on Room.Residence_Hall_idResidence_Hall = idResidence_Hall where Lottery_idLottery = %d and Residence_Hall_idResidence_Hall = idResidence_Hall;' % (lottery), False)
    for result in results:
        numAvailable[result[0]] = result[1]
    return numAvailable
    
def processAndSend(results, lottery, numSlots):
    firstDict = results[0][0][0]
    startTime = sendQuery('SELECT StartTime FROM Lottery WHERE idLottery = %d;' % (lottery), False)[0][0]
    timeBetween = sendQuery('SELECT timeBetween FROM Lottery WHERE idLottery = %d;' % (lottery), False)[0][0]
    startTime = datetime.strptime(startTime, '%I:%M')
    currentTime = startTime

    rooms = {}
    for key, value in firstDict.items():
        rooms[key] = 0
    
    maxResultLength = 0
    for result in results:
        if len(result) > maxResultLength:
            maxResultLength = len(result)

    k =0
    while k < maxResultLength:
        tempRooms = dict(rooms)
        i = 0
        while i < len(results):
            for key, value in firstDict.items():
                if k < len(results[i]):
                    for time in results[i][k]:
                        if time is not None and time[key]:
                            tempRooms[key] = tempRooms[key] + 1
            i = i+1
        k = k + 1

        for key, value in tempRooms.items():
            percentOccupied = float(value)/float(NUMBER_OF_REPS * numSlots)
            tables = 'INSERT INTO ModelData (Room_id, Time, probability) '
            values = 'VALUES (%d, "%s", %f) ' % (key, str(currentTime.time())[0:5], percentOccupied)
            update = 'ON DUPLICATE KEY UPDATE probability = %f;' % (percentOccupied)
            query = tables + values + update
            sendQuery(query, True)

        print("%s added to model" % (str(currentTime.time())[0:5]))
        currentTime = currentTime + timedelta(minutes=timeBetween)
        

        
        
        

if __name__ == '__main__':
    main()