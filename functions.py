import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tweets import tweets

def get_latest_bitcoin_price(ticker):
    df =yf.download(ticker, period='1d', interval='1m')
    bitcoinPrice = df['Close'].iloc[-1]
    time = dt.datetime.fromtimestamp(int(round(df.index[-1].timestamp())))

    return [time, bitcoinPrice]

def get_bitcoin_data(ticker, minDate, maxDate, column):
    df = yf.download(ticker, start=minDate, end=maxDate, interval="1h")
    if column: return df[column]
    else: return df

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
    df.rename(columns={"num_coins":"Number of Coins", "bitcoin_price":"Bitcoin Price",
                        "original_cost":"Investment Cost","current_investment":"Current Investment",
                        "gain/loss":"Gain/Loss","pct gain/loss":"% Gain/Loss"},
                        inplace=True)
    html = df.style.applymap(color_return, subset=['Gain/Loss', '% Gain/Loss'])\
                .set_table_attributes('id="tweet-table"')\
                .format(precision=2, na_rep='MISSING', thousands=",", formatter={('% Gain/Loss') : "{:.2f} %"})\
                .format("${:,.2f}", na_rep='MISSING', subset=['Bitcoin Price', 'Investment Cost','Current Investment','Gain/Loss'])\
                .hide_index()\
                .set_properties(**{'width': '150 px'}, subset=['Tweet'],)\
                .render()
    return html

def color_return(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

def portfolio_return(df):
    """
    Portfolio Return
        Sum of investment weight * investment return
        Calculate investment weight using df['Column'].sum()
    """

    costTotal = df['Investment Cost'].sum()
    df['Weight'] = df.apply(lambda x: (x['Investment Cost']/costTotal), axis=1)
    df['W*R'] = df.apply(lambda x: x['Weight'] * x['% Gain/Loss'], axis=1)
    portfolio_return = {"return": df['W*R'].sum(),
                        "totalCost": costTotal,
                        "string":f'The government of Nayib Bukele has invested a total of ${costTotal:,.2f}\n With an expected return of unrealized gains/losses of {df["W*R"].sum():,.2f}%'}
    return portfolio_return


## Plotting

def create_plot():
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    return fig

#Plot a line chart with High as value
def line_chart(df, fig):
    line = {
        'x': df.index,
        'y': df.Close,
        'type': 'scatter',
        'line':{
            'color': 'black'},
        'name': 'Close',
    }

    fig.add_trace(line, secondary_y=False )


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
#