import pandas as pd
import yfinance as yf
from Historic_Crypto import HistoricalData
import datetime as dt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tweets import tweets
import datetime

def get_latest_bitcoin_price(ticker):
    df =yf.download(ticker, period='1d', interval='1m')
    bitcoinPrice = df['Close'].iloc[-1] if df.shape[0] > 1 else df['Close'].iloc[0]
    time = dt.datetime.fromtimestamp(int(round(df.index[-1].timestamp())))
    return [time, bitcoinPrice]


def get_historical_bitcoin(ticker, granularity, start_date, end_date, column):
    try:
        df = pd.read_pickle('./historic.pkl')
    except Exception as e:
        print(e)
        df = HistoricalData(ticker, granularity, start_date.strftime('%Y-%m-%d-%H-%M'), end_date.strftime('%Y-%m-%d-%H-%M')).retrieve_data()
        df.index = df.index.tz_localize('UTC')
        df.to_pickle('./historic.pkl')
    if df.index.max().strftime('%Y-%m-%d %H:00:00') != end_date.strftime('%Y-%m-%d %H:00:00'):
        print('MISSING DATA')
        start = df.index.max()
        print(f'getting data from {start} - {end_date}')
        missing = HistoricalData(ticker, granularity, start.strftime('%Y-%m-%d-%H-%M'), end_date.strftime('%Y-%m-%d-%H-%M')).retrieve_data()
        df = pd.concat([df, missing])
    else: print('NO MISSING DATA')
    if column: return df[column]
    else: return df

def get_bitcoin_data(ticker, minDate, maxDate, column, interval):
    df = yf.download(ticker, start=minDate, end=maxDate, interval=interval)
    if column: return df[column]
    else: return df

def get_bitcoin_price(tweets, bitHourly):
    #Identify price of tweet
    for tweet in tweets:
        date = tweets[tweet]['date']
        date = pd.Timestamp(date, tz='America/El_Salvador').tz_convert('UTC')
        bitPrice = bitHourly.iloc[bitHourly.index.get_indexer([date], method='nearest')][0]
        tweets[tweet]['bitcoin_price'] = bitPrice

    #Return tweets
    return tweets

def get_daily_bitcoin(tweets, bitDaily):
    last = list(tweets)[-1]
    bit_per_day = tweets[last]
    bit_per_day_date = bit_per_day['date']
    latest = last
    tweetsDaily = {}
    for day in range(1, int((pd.Timestamp.today() - bit_per_day_date).days)):
        date = pd.to_datetime((bit_per_day_date + datetime.timedelta(days=day))).strftime('%Y-%m-%d')
        latest += 1
        bitPrice = bitDaily.iloc[bitDaily.index.get_indexer([date], method='nearest')][0]
        tweetsDaily[latest] = {'date': pd.to_datetime((bit_per_day_date + datetime.timedelta(days=day)).strftime('%Y-%m-%d')),
                            'link':'https://twitter.com/nayibbukele/status/1593113857261965312?s=46&t=lTdkuYKDUQ6KKCYNpKuVIQ',
                            'num_coins':1,
                            'bitcoin_price': bitPrice}
    return tweetsDaily

def get_investment_value(tweets, latestBitPrice):
    currentPrice = latestBitPrice
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

def add_daily(dailyDf):
    #Summarize dailyDf
    summary = {
        'date':dailyDf.iloc[0].date,
        'link':dailyDf.iloc[0].link,
        'num_coins': dailyDf['num_coins'].sum(),
        'bitcoin_price': np.average(a = dailyDf['bitcoin_price'], weights= dailyDf['num_coins']),
        'original_cost': dailyDf['original_cost'].sum(),
        'current_investment':  dailyDf['current_investment'].sum(),
        'gain/loss': dailyDf['gain/loss'].sum(),
        'pct gain/loss':((dailyDf['current_investment'].sum()- dailyDf['original_cost'].sum())/dailyDf['original_cost'].sum())*100
    }
    return summary

def format_df(df, summary=False):
    df.insert(0, 'Tweet', df.apply( lambda row: f'<a target="_blank" href="{row.link}" style="text-decoration:none;"> &#128197; {row.date.strftime("%Y %b %d %H:%M %Z")} CST</a>', axis=1 ))
    if summary == True:
        tail = df.tail(1)
        df.loc[df.index[-1], 'Tweet'] = f'<a target="_blank" href="{df.loc[df.index[-1], "link"]}" style="text-decoration:none;"> &#128197; {df.loc[df.index[-1], "date"].strftime("%Y %b %d %H:%M %Z")} CST (&#128260; purchase)</a>'
    df.drop(['link', 'date'], axis=1, inplace=True)
    df.rename(columns={"num_coins":"# of Bitcoin", "bitcoin_price":"Bitcoin Price",
                        "original_cost":"Cost","current_investment":"Current Value",
                        "gain/loss":"P/L","pct gain/loss":"% P/L"},
                        inplace=True)

    df.loc['Total'] = df.iloc[:, :-1].sum()
    df.loc['Total', 'Tweet'] = '<b>Total<b>'
    df.loc['Total', 'Bitcoin Price'] = np.average(a = df['Bitcoin Price'][:-1], weights= df['# of Bitcoin'][:-1])
    df.loc['Total', '% P/L'] = ((df.loc['Total', 'Current Value']- df.loc['Total', 'Cost'])/df.loc['Total', 'Cost'])*100
    df['# of Bitcoin'] = df['# of Bitcoin'].apply(lambda x: f"₿ {x:,.0f}")

    df['P/L']=df['P/L'].apply(lambda x: f"$({abs(x):,.2f})" if (x)<0 else f"${x:,.2f}")
    return df

def df_to_html(df):
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
    df = df.iloc[:-1,:].copy()
    costTotal = df["Cost"].sum()
    df['Weight'] = df.apply(lambda x: (x["Cost"]/costTotal), axis=1)
    df['W*R'] = df.apply(lambda x: x['Weight'] * x['% P/L'], axis=1)

    portfolio_return = {"return": df['W*R'].sum(),
                        "current": df['Current Value'].sum(),
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

    get_daily_bitcoin(tweets)
    # tweetsData = get_bitcoin_price(tweets)
    # tweetsData = get_investment_value(tweetsData)

    # tweetsDf = format_df(dict_to_df(tweetsData))
    # # print(tweetsDf)

    # #Calculate gain/loss return from investment
    # bitPrice = get_latest_bitcoin_price('BTC-USD')


#To-Do:
# * Gain/Loss of Tweet
# * TZ for latest price retrieved
# * Add disclaimer of delay in latest price & not included transaction costs
#
