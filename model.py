MYSQL_CONFIG = {
  'user': 'admin',
  'password': '1387194#',
  'host': 'database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com',
  'database': 'Capstone',
  'raise_on_warnings': True
}

NUMBER_OF_REPS = 100

import mysql.connector
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
from scipy.stats import hypergeom
import random


def sendQuery(query):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    curA = conn.cursor()
    curA.execute(query)
    results = curA.fetchall()
    conn.commit()
    conn.close()
    return results

def main():
    lotteries = getLotteries()
    for lottery in lotteries:
        probs = getProbs(lottery)
        finalprobs = getOverallProbs(probs)
        numSlots = sendQuery('SELECT numSlots FROM Lottery WHERE idLottery = %d' % (lottery))[0][0]
        results = doModel(finalprobs, numSlots)
        processAndSend(results, lottery, numSlots)

def getLotteries():
    lotteries = []
    query = 'SELECT idLottery FROM Lottery'
    temp = sendQuery(query)
    for lottery in temp:
        lotteries.append(lottery[0])
    return lotteries

def getProbs(lottery):
    currentYear = datetime.now().year

    dataYear = currentYear - 1
    data = ['dummy']
    probs = []
    while dataYear >= currentYear - 6 and len(data)>0:
        query = 'SELECT Room_id, SampleData.Time, SampleData.Slot from SampleData INNER JOIN Room on SampleData.Room_id = Room.id INNER JOIN Residence_Hall on Room.Residence_Hall_idResidence_Hall = idResidence_Hall where Lottery_idLottery = %d and SampleData.Year = %d' % (lottery, dataYear) 
        data = sendQuery(query)
        if len(data) > 0:
            probs.append(processYear(data))
        dataYear = dataYear -1
    return probs
    
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
            query = 'SELECT COUNT(Room_id) from SampleData where Room_id = %d' % (int(roomId))
            count =sendQuery(query)
            totalNumber[roomId] = count[0][0]
            numberInFirst[roomId] = 1
            total = total + 1
    
    for roomId in numberInFirst:
        probablity[roomId] = numberInFirst[roomId]/total
    return probablity

def getOverallProbs(listProbs):
    if len(listProbs) == 1:
        return listProbs[0]
    elif len(listProbs) == 2:
        return (.75 * listProbs[0]) + (.5 * listProbs[1])
    elif len(listProbs) == 3:
        return (.66 * listProbs[0]) + (.34 * listProbs[1]) + (.33 * listProbs[2])
    elif len(listProbs) == 4:
        return (.5 * listProbs[0]) + (.17 * listProbs[1]) + (.16 * listProbs[2]) + (.16 * listProbs[3])
    elif len(listProbs) == 4:
        return (.5 * listProbs[0]) + (.125 * listProbs[1]) + (.125 * listProbs[2]) + (.125 * listProbs[3])+ (.125 * listProbs[4])


def doModel(probs, numSlots):
    numAvailable = getTotalAvailableRooms(probs)
    modelRuns = []
    for i in range(0,NUMBER_OF_REPS):
        tempProbs = dict(probs)
        tempNumAvailable = dict(numAvailable)
        modelRuns.append(modelRun(tempProbs, tempNumAvailable, numSlots))
    return modelRuns
        
#Adjust Probs method needs to be added
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
            availableRow.append(getCurrentAvailability(probs))
            if rand1 >= hvar and anotherRow:
                room = roomPicker(probs)
                numAvailable[room] = numAvailable[room] -1
                if numAvailable[room] == 0:
                    probs, anotherRow = adjustProbs(probs, room)

        available.append(availableRow)     
        i = i+1     
    return available   

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

def getCurrentAvailability(probs):
    if probs is None:
        return None
    available = {}
    for key, value in probs.items():
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

def getTotalAvailableRooms(probs):
    numAvailable = {}
    for key, value in probs.items():
        count = sendQuery('SELECT numAvailable FROM Room WHERE id = %d' % (key))
        numAvailable[key] = count[0][0]
    return numAvailable
    
def processAndSend(results, lottery, numSlots):
    firstDict = results[0][0][0]
    startTime = sendQuery('SELECT StartTime FROM Lottery WHERE idLottery = %d' % (lottery))[0][0]
    timeBetween = sendQuery('SELECT timeBetween FROM Lottery WHERE idLottery = %d' % (lottery))[0][0]
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
            update = 'ON DUPLICATE KEY UPDATE probability = %f' % (percentOccupied)
            query = tables + values + update
            sendQuery(query)

        print("%s added to model" % (str(currentTime.time())[0:5]))
        currentTime = currentTime + timedelta(minutes=timeBetween)
        

        
        
        

if __name__ == '__main__':
    main()