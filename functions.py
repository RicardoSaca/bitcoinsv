from cProfile import label
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tweets import tweets
from datetime import timezone

def get_latest_bitcoin_price(ticker):
    df =yf.download(ticker, period='1d', interval='1m')
    bitcoinPrice = df['Close'].iloc[-1] if df.shape[0] > 1 else df['Close'].iloc[0]
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
        date = tweets[tweet]['date']
        date = pd.Timestamp(date, tzinfo=timezone.utc)
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
    df.insert(0, 'Tweet', df.apply( lambda row: f'<a target="_blank" href="{row.link}" style="text-decoration:none;"> &#128197; {row.date.strftime("%Y %b %d %H:%M %Z")} CST</a>', axis=1 ))
    df.drop(['link', 'date'], axis=1, inplace=True)
    df.rename(columns={"num_coins":"Amount of Bitcoin", "bitcoin_price":"Bitcoin Price",
                        "original_cost":"Cost","current_investment":"Current Value",
                        "gain/loss":"P/L","pct gain/loss":"% P/L"},
                        inplace=True)
    df.loc['Total'] = df.iloc[:, :-1].sum()
    df.loc['Total', 'Tweet'] = '<b>Total<b>'
    df.loc['Total', '% P/L'] = ((df.loc['Total', 'Current Value']- df.loc['Total', 'Cost'])/df.loc['Total', 'Cost'])*100
    df['Amount of Bitcoin'] = df['Amount of Bitcoin'].apply(lambda x: f"₿ {x:,.0f}")


    df['P/L']=df['P/L'].apply(lambda x: f"$({abs(x):,.2f})" if (x)<0 else f"${x:,.2f}")

    last_row = pd.IndexSlice[df.index[df.index == "Total"], :]

    html = df.style.applymap(color_return_int, subset=['% P/L'])\
                .applymap(color_return_str, subset=['P/L'])\
                .applymap(style_bold, subset=last_row)\
                .set_table_attributes('id="tweet-table"')\
                .format(precision=2, na_rep='MISSING', thousands=",", formatter={('% P/L') : "{:.2f} %"})\
                .format("${:,.2f}", na_rep='MISSING', subset=['Bitcoin Price', 'Cost','Current Value'])\
                .hide(axis='index')\
                .set_properties(**{'width': '150 px'}, subset=['Tweet'],)\
                .to_html()
    return html

def negative_numbers(val):
    return f'${str(val)}' if val >= 0 else f'$({abs(val)})'

def color_return_str(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """

    color = 'red' if val.startswith('$(') else 'green'
    return 'color: %s' % color

def color_return_int(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

def style_bold(val):
    return "font-weight: bold"

def portfolio_return(df):
    """
    Portfolio Return
        Sum of investment weight * investment return
        Calculate investment weight using df['Column'].sum()
    """
    costTotal = df['original_cost'].sum()
    df['Weight'] = df.apply(lambda x: (x['original_cost']/costTotal), axis=1)
    df['W*R'] = df.apply(lambda x: x['Weight'] * x['pct gain/loss'], axis=1)

    portfolio_return = {"return": df['W*R'].sum(),
                        "current": df['current_investment'].sum(),
                        "totalCost": costTotal,
                        }
    df.drop(labels=['Weight', 'W*R'], axis=1, inplace=True)
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
        'fill':'tozeroy',
        'line':{
            'color': 'green' if df.Close[0] < df.Close[-1] else 'red'},
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
