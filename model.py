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
    while dataYear > currentYear - 6 and len(data)>0:
        query = 'SELECT * from SampleData where Year = %d' % (dataYear)
        data = sendQuery(query)
        query = 'SELECT '
        if len(data) > 0:
            probs.append(processYear(data, dataYear))
        dataYear = dataYear -1

def processYear(data, year):
    totalNumber = {}
    numberInFirst = {}
    data = sorted(data, key= itemgetter(2,3))
    for record in data:
        print(record)
    

if __name__ == '__main__':
    main()