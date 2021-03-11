MYSQL_CONFIG = {
  'user': 'admin',
  'password': '1387194#',
  'host': 'database-1.ceb0m91rauea.us-east-1.rds.amazonaws.com',
  'database': 'Capstone',
  'raise_on_warnings': True
}

import mysql.connector
import datetime
from operator import itemgetter
from scipy.stats import hypergeom

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
        print(numSlots)
        doModel(finalprobs, numSlots)

def getLotteries():
    lotteries = []
    query = 'SELECT idLottery FROM Lottery'
    temp = sendQuery(query)
    for lottery in temp:
        lotteries.append(lottery[0])
    return lotteries

#make it only come from lottery
def getProbs(lottery):
    allYears = []
    currentYear = datetime.datetime.now().year

    dataYear = currentYear - 1
    data = ['dummy']
    probs = []
    while dataYear >= currentYear - 6 and len(data)>0:
        query = 'SELECT Room_id, SampleData.Time, SampleData.Slot from SampleData where Year = %d' % (dataYear) 
        data = sendQuery(query)
        query = 'SELECT '
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
    while len(probs) > 0:
        dist = hypergeom(1000, 24, 1)
        


def getTotalAvailableRooms(probs):
    numAvailable = {}
    for key, value in probs.items():
        count = sendQuery('SELECT numAvailable FROM Room WHERE id = %d' % (key))
        numAvailable[key] = count[0][0]
    return numAvailable
    

if __name__ == '__main__':
    main()