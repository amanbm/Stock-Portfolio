import datetime as dt 
from datetime import date
import pandas as pd
import pandas_datareader.data as web
import os.path

stabilityDict = {
	6: "rock solid",
	10: "stable",
	25: "moderate",
	45: "volatile",
	49: "highly volatile"
}


def getUpdatedTickers():
	with open("portfolio.txt", "r") as f:
		alltickers = f.read().split()
		f.close()
	return alltickers


def getStability(percentChange):
	for percent in stabilityDict:
		if(percentChange < percent):
			return stabilityDict[percent]
	return stabilityDict[45]

# check if csv file for a certain ticker symbol exists, if so, read from the file instead of making a new query
def getUpdatedData(ticker, start, end, force):
	dataPath = './data/'+ticker.upper()+'.csv'
	if(force or not os.path.isfile(dataPath)):
		df = web.DataReader(ticker, 'yahoo', start, end)
		df.to_csv(dataPath)
		return getUpdatedData(ticker, start, end, False)
	else: 
		return pd.read_csv(dataPath, parse_dates=True, index_col=0)
	

# Returns the most recent valid business day
def getValidCurrDate():
	if(date.today().weekday() > 4):
		today = date.datetime(2019, 9, 9)
		offset = max(1, (today.weekday() + 6) % 7 - 3)
		timedelta = date.timedelta(offset)
		most_recent = today - timedelta
		return most_recent
	else:
		return date.today()


def printSummary(start, end):
	for ticker in getUpdatedTickers():
		print(ticker.upper())

		#TODO Optimize (maybe cache this result somehow)
		df = getUpdatedData(ticker, start, end, False)
		high = df.loc[:]['High'].max()
		low = df.loc[:]['Low'].min()
		delta = high - low
		percentChange = (delta/((high+low)/2))*100
		print(getStability(percentChange))
		print("High: " + str(round(high, 2)) + "\nLow: " + str(round(low, 2)) + "\nDelta: " + str(round(delta, 2)))
		print("Percent Change: " + str(int((percentChange).round())) + "%")
		print('\n')


def printRecommendations(weeks_preceding):
	percentMap = {}
	for ticker in getUpdatedTickers():
		##TODO bug: this program doesn't work M-Th after 11:59pm
		end = getValidCurrDate()
		start = end - dt.timedelta(weeks=weeks_preceding)

		df = getUpdatedData(ticker,start,end, False)

		try:
			endPrice = round(df.loc[str(end)]['Close'], 2)
			startPrice = round(df.loc[str(start)]['Close'], 2)
		except:
			print("fetching data for " + ticker.upper() + "...")
			df = getUpdatedData(ticker,start,end,True)

		try:
			endPrice = round(df.loc[str(end)]['Close'], 2)
			startPrice = round(df.loc[str(start)]['Close'], 2)
		except:
			print("fix this bug, today does not have any data")
			
		##
		# print("start: " + str(start) + " " + "end: " + str(end))
		# print(str(startPrice) + " " + str(endPrice))
		##

		percentChange = round(((endPrice-startPrice)/startPrice)*100, 2)
		rec = ""
		if(percentChange <= -2):
			rec = "Buy"
		elif(percentChange >=2):
			rec = "Sell"
		else:
			rec = "Hold"

		percentMap[ticker.upper()] = [percentChange, rec]

	print("buys(b)/sells(s)/holds(h): ")
	answer = input().upper()


	for element in percentMap:
		if(percentMap[element][1][0] == answer):
			print(str(percentMap[element][1]) + " " + element + " (" + str(percentMap[element][0]) + "%) ")

# start_date_entry = input('Enter a start date in YYYY-MM-DD format: ')
# year, month, day = map(int, start_date_entry.split('-'))
# date1 = dt.date(year, month, day)

# end_date_entry = input('Enter an end date in YYYY-MM-DD format: ')
# year, month, day = map(int, end_date_entry.split('-'))
# date2 = dt.date(year, month, day)


print("How many weeks prior would you like data for? ")
inp = input()
printRecommendations(int(inp))
print("quit(q) or continue(c)")

while(1):
	inp = input()
	if(inp == "q"):
		exit()
	elif(inp == "c"):
		print("How many weeks prior would you like data for?")
		inp = input()
		printRecommendations(int(inp))
	else:
		print("incorrect input")

	print("quit(q) or continue(c)")

