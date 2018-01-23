import json
import requests
import cryptocompare
import datetime
import time
from time import sleep
from binance.client import Client
import csv
from pathlib import Path

# todo: add the big coins as reference
# add 24 hr avg
#global variables

max = 0
min = 0
myCoinList=[]
myHigh=[]
myLow=[]

#check one to make sure response is less than 1000ms
def print_binance_local_time_difference():
    print ("Please wait, ensuring Server Connection is possible...")
    avg = 0
    for i in range(1, 5):
        local_time1 = int(time.time() * 1000)
        server_time = client.get_server_time()
        diff1 = server_time['serverTime'] - local_time1
        local_time2 = int(time.time() * 1000)
        diff2 = local_time2 - server_time['serverTime']
        avg += diff2
        #print("local1: %s server:%s local2: %s diff1:%s diff2:%s" % (
        #local_time1, server_time['serverTime'], local_time2, diff1, diff2))
        print("checking...")
        time.sleep(2)
    return avg/4

def createFile(list_coins):
    print("Checking for file...")
    my_file = Path("binance_info.txt")
    if my_file.is_file():
        print ("File already exist.")
        return
    else:
        print ("File doesn't exist, creating file.")
        initial_value = 0
        file = open("binance_info.txt","w+")
        count = 0
        count_coins=0
        length = len(list_coins)*3+2
        while count<length:
            if (count%3+1)%3!=0:
                file.write(str(initial_value))
                if count<length-1:
                    file.write(',')
            if (count%3+1)%3==0:
                file.write(str(list_coins[count_coins]))
                file.write(',')
                count_coins+=1
            count+=1
        file.close()
    return

def readFile():
    print("Reading File...")
    value_list = []
    file = open("binance_info.txt", "r")
    reader = csv.reader(file)
    for line in reader:
        value_list = line
    return value_list
    file.close()

def createList(val_list):
    print("Setting necessary variables...")
    count=2
    global max
    global min
    global myCoinList
    global myHigh
    global myLow
    max = float(val_list[0])
    min = float(val_list[1])
    while count < (len(val_list)):
        myCoin.append(val_list[count])
        myHigh.append(float(val_list[count + 1]))
        myLow.append(float(val_list[count + 2]))
        count += 3

def printNewValues(_max, _min, _myCoin, _myHigh, _myLow):
    val = []
    val.append(str(_max))
    val.append(str(_min))
    count = 0
    while count < len(_myCoin):
        val.append(str(_myCoin[count]))
        val.append(str(_myHigh[count]))
        val.append(str(_myLow[count]))
        count += 1

    #print(values)
    count = 0
    printFile = open("binance_info.txt", "w")
    while count < len(val):
        printFile.write(val[count])
        if count != len(val) - 1:
            printFile.write(',')
        count += 1

    print("File written")

#new list of current worth vs the saved one, return to other list
def compareHigh(high, low, newList):
    count =0
    while count<len(high):
        if high[count]<newList[count]:
            high[count] = newList[count]
        if low[count]>newList[count]:
            low[count] = newList[count]
        count+=1
    return high, low

def min_max (min, max, val):
    if min>val:
        min = val
    if max<val:
        max = val
    return min, max
# place your keys here from Bianance
api_key = ''
secret_key = ''
client = Client(api_key, secret_key)

# Enter coin in caps, between '', seperated by comma
myCoin = ['XRP', 'VIBE', 'XVG', 'ADA', 'XLM']
createFile(myCoin)
values = readFile()
createList(values)
# enter whatever currency you prefer, i.e. EUR
exchange = 'USD'
# enter whatever exchange you prefer, i.e. BTC
exchangeCoin = 'ETH'
amtInvested = 1250

var_minutes = .5
var_time = var_minutes * 60
iterations = 24 * 60 / var_minutes
upToIterations = 0
# add column after worth with change from previous interval

previousVal = []
previousWorth = []
for i in myCoin:
    previousVal.append(0)
    previousWorth.append(0)

avg = print_binance_local_time_difference()
print("Avg response time: {0}".format(avg))
if avg<1000:
    print("Starting script...")
else:
    print("Response time too great, try again later...")
while True and avg<1000:
    count = 0
    exchangeValue = '0'
    # array with current values of coin at your exchange
    currentVal = []
    # set the iteration back to 0 since we are only checking every 24 hr iterations
    if upToIterations == iterations:
        upToIterations = 0
        print ("24 hours have passed")
    if upToIterations == (iterations/2):
        printNewValues(max, min, myCoin, myHigh, myLow)
        print ("Saving values to File")
    # finds the rate for coin to USD or whatever variable exchange is from crytocompare
    while count < len(myCoin):
        coin_toUSD = cryptocompare.get_price(myCoin[count], curr=exchange, full=False)
        coin_dumps = json.dumps(coin_toUSD)  # dict
        coin_loads = json.loads(coin_dumps)  # list
        # add to array, change complexity
        currentVal.append(coin_loads[myCoin[count]][exchange])
        if upToIterations == 0:
            previousVal[count] = currentVal[count]
        # iterate
        count += 1

    # call to binance api, gets all current prices
    prices = client.get_all_tickers()
    price = json.dumps(prices)
    prices_list = json.loads(price)

    # timestamp
    timeStamp = time.time()
    currentTime = datetime.datetime.fromtimestamp(timeStamp).strftime('%m-%d-%Y %H:%M:%S')
    print("Iteration {0} of {1:5.0f}".format(upToIterations + 1, iterations))
    print(currentTime)

    count = 0
    totalBalance = 0
    # header
    print("{0:7} {1:15} {2:>10} {3:>10} {4:>10} {5:>10} {6:>10} {7:>10} {8:>10}".format("Coin", "Balance", exchangeCoin, exchange,
                                                                        "Worth", exchange + " CHG", "Worth CHG", "Low","High"))
    print("----------------------------------------------------------------------------------------------------------------------")
    while count < len(myCoin):
        exchangeName = myCoin[count] + exchangeCoin  # needed to find the correct price in bianance list
        # for loop
        for i in prices_list:
            if i['symbol'] == exchangeName:
                exchangeValue = i['price']
            # dict to list coversion
        balance = client.get_asset_balance(asset=myCoin[count])
        bal = json.dumps(balance)
        parsed_balance = json.loads(bal)
        worth = float(parsed_balance['free']) * float(currentVal[count])  # multiple coins by exchange worth xrp * usd
        if upToIterations == 0:
            previousWorth[count] = worth
        totalBalance += worth
        print("{0:7} {1:15} {2:10} {3:10} {4:>10.2f} {5:>10.5f} {6:10.2f} {7:10} {8:10}".format(parsed_balance['asset'],
                                                                                  parsed_balance['free'], exchangeValue,
                                                                                  currentVal[count], worth,
                                                                                  currentVal[count] - previousVal[
                                                                                      count],
                                                                                  worth - previousWorth[count], myHigh[count], myLow[count]))
        # previousVal[count] = currentVal[count]
        count += 1

    myHigh, myLow = compareHigh(myHigh, myLow, currentVal)
    min, max = min_max(min, max, totalBalance-amtInvested)
    print("{0:7} {1:15} {2:>10} {3:>10} {4:>10.2f}".format("", "", "", "Total:", totalBalance))
    print("{0:7} {1:15} {2:>10} {3:>10} {4:>10.2f}".format("", "", "", "Gross:", totalBalance - amtInvested))
    print("{0:7} {1:15} {2:>10} {3:>10} {4:>10.2f}".format("", "", "", "Lowest:", min))
    print("{0:7} {1:15} {2:>10} {3:>10} {4:>10.2f}".format("", "", "", "Highest:", max))

    upToIterations += 1
    sleep(var_time)


