from operator import index
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from functions import dict_to_df, get_bitcoin_price, get_investment_value, get_latest_bitcoin_price, format_df, portfolio_return
from tweets import tweets

st.set_page_config(layout="wide")

st.title("Inversion del Gobierno de El Salvador en Bitcoin")


bitPrice = get_latest_bitcoin_price('BTC-USD')

f'The current price of Bitcoin is ${bitPrice[1]:,.2f} extracted at {bitPrice[0].strftime("%Y-%b-%d %H:%M %Z")}'

tweetsData = get_bitcoin_price(tweets)
tweetsData = get_investment_value(tweetsData)

tweetsDf = dict_to_df(tweetsData)

tweetsHtml = format_df(tweetsDf)
with st.container():
    st.write(tweetsHtml, unsafe_allow_html=True)

with st.container():
    port_return = portfolio_return(tweetsDf)
    st.subheader(f'The government of Nayib Bukele has invested a total of ${port_return["totalCost"]:,.2f} of tax payer money in Bitcoin.')
    st.subheader(f'These investments have an Unrealized {"Loss" if port_return["return"] < 0 else "Gain"} of {port_return["return"]:+,.2f} %')
    st.text('* The calculations above exclude commission rates, transaction costs, and any other costs undisclosed by the governments.')