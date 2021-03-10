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
        data = getData(lottery)

def getLotteries():
    lotteries = []
    query = 'SELECT idLottery FROM Lottery'
    temp = sendQuery(query)
    for lottery in temp:
        lotteries.append(lottery[0])
    return lotteries

def getData(lottery):
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
            probs.append(processYear(data, dataYear))
        dataYear = dataYear -1

def processYear(data, year):
    totalNumber = {}
    numberInFirst = {}
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
            numberInFirst[roomId] = count[0][0]
    print(numberInFirst)
    

if __name__ == '__main__':
    main()