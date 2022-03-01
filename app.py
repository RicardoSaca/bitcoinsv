import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from functions import dict_to_df, get_bitcoin_price, get_investment_value, get_latest_bitcoin_price, format_df
from tweets import tweets

st.title("Inversion del Gobierno de El Salvado en Bitcoin")


bitPrice = get_latest_bitcoin_price('BTC-USD')

f'The current price of Bitcoin is ${bitPrice[1]:,.2f} extracted at {bitPrice[0].strftime("%Y-%b-%d %H:%M %Z")}'

tweetsData = get_bitcoin_price(tweets)
tweetsData = get_investment_value(tweetsData)

# tweetsDf = dict_to_df(tweetsData)
tweetsDf = format_df(dict_to_df(tweetsData))

pd.set_option('display.max_colwidth', -1)

st.dataframe(tweetsDf)

tweetsDf = tweetsDf.to_html(escape=True)

st.write(tweetsDf, unsafe_allow_html=True)


