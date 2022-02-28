from xml.dom import minidom
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from tweets import tweets

def set_ticker(ticker):
    stock = yf.Ticker(ticker)
    return stock

def get_bitcoin_data(ticker, minDate, maxDate, column):
    df = yf.download(ticker, start=minDate, end=maxDate, interval="1h")
    return df[column]

def get_bitcoin_price(tweet):
    date = tweet['date']
    startDate = date + dt.timedelta(hours=-1)
    endDate = date + dt.timedelta(hours=1)
    df = yf.download(tickers='BTC-USD', start=startDate, end=endDate, interval='1m')
    print(df)

def main():

    minDate = tweets[min(tweets, key=lambda x:tweets[x]['date'])]['date']
    maxDate = tweets[max(tweets, key=lambda x:tweets[x]['date'])]['date']

    df = get_bitcoin_data("BTC-USD", minDate, maxDate, "Close")
    print(type(pd.Timestamp(tweets[1]['date'])), type(df.index[1]))
    print(df.index)
    price =[]
    for tweet in tweets:
        date = tweets[tweet]['date'].strftime('%Y-%m-%d %H:00:00+00:00')
        date = pd.Timestamp(date)
        print(type(date))
        # print(date, df.loc(date))
        print(df['2021-09-07 17:00:00+00:00'])
        # price.append([date, df[date]])


main()