import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from tweets import tweets

def get_latest_bitcoin_price(ticker):
    df =yf.download(ticker, period='1d', interval='1m')
    bitcoinPrice = df['Close'].iloc[-1]
    time = dt.datetime.fromtimestamp(int(round(df.index[-1].timestamp())))

    return [time, bitcoinPrice]

def get_bitcoin_data(ticker, minDate, maxDate, column):
    df = yf.download(ticker, start=minDate, end=maxDate, interval="1h")
    return df[column]

def get_bitcoin_price(tweets):
    #Set min and max date from tweets dictionary
    minDate = tweets[min(tweets, key=lambda x:tweets[x]['date'])]['date'].replace(second=0, hour=0, minute=0)
    maxDate = tweets[max(tweets, key=lambda x:tweets[x]['date'])]['date'].replace(second=0, hour=0, minute=0) + dt.timedelta(days=1)

    #Retrieve bitcoin close data by the hour
    df = get_bitcoin_data("BTC-USD", minDate, maxDate, "Close")

    #Identify price of tweet
    for tweet in tweets:
        date = tweets[tweet]['date'].strftime('%Y-%m-%d %H:00:00+00:00')
        date = pd.Timestamp(date)
        bitPrice = df.iloc[df.index.get_indexer([date], method='nearest')][0]
        tweets[tweet]['bitcoin_price'] = bitPrice

    #Return tweets
    return tweets

def get_investment_value(tweets):

    currentPrice = get_latest_bitcoin_price("BTC-USD")[1]
    for tweet in tweets:
        purchasedPrice = tweets[tweet]['bitcoin_price']
        numCoins = tweets[tweet]['num_coins']
        tweets[tweet]['original_cost'], tweets[tweet]['current_investment'], tweets[tweet]['gain/loss'], tweets[tweet]['pct gain/loss'] = get_gain_loss(currentPrice, purchasedPrice, numCoins)

    return tweets

def get_gain_loss(currentPrice, purchasedPrice, numCoins):
    originalCost = numCoins * purchasedPrice
    currentInvestment = numCoins * currentPrice
    gainLoss = currentInvestment - originalCost
    pctGainLoss = ((currentInvestment - originalCost)/originalCost) * 100

    return originalCost, currentInvestment, gainLoss, pctGainLoss



def dict_to_df(tweets):
    tweetsDf = pd.DataFrame.from_dict(tweets, orient='index')
    return tweetsDf

def format_df(df):
    df.insert(0, 'Tweet', df.apply( lambda row: f'<a target="_blank" href="{row.link}">{row.date.strftime("%Y-%b-%d %H:%M %Z")}</a>', axis=1 ))
    df.drop(['link', 'date'], axis=1, inplace=True)
    df.rename(columns={"num_coins":"Number of Coins", "bitcoin_price":"Bitcoin Price", "original_cost":"Investment Cost","gain/loss":"Gain/Loss","pct gain/loss":"% Gain/Loss"}, inplace=True)
    return df

if __name__ == "__main__":

    tweetsData = get_bitcoin_price(tweets)
    tweetsData = get_investment_value(tweetsData)

    tweetsDf = format_df(dict_to_df(tweetsData))
    print(tweetsDf)
    #Calculate gain/loss return from investment
    bitPrice = get_latest_bitcoin_price('BTC-USD')


#To-Do:
# * Gain/Loss of Tweet
# * TZ for latest price retrieved
# * Add disclaimer of delay in latest price & not included transaction costs
