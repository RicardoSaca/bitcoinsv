from operator import index
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from functions import dict_to_df, get_bitcoin_data, get_bitcoin_price, get_investment_value, get_latest_bitcoin_price, format_df, portfolio_return, create_plot, line_chart
from tweets import tweets

st.set_page_config(layout="wide")

st.title("El Salvador's Government Bitcoin Investment")


bitPrice = get_latest_bitcoin_price('BTC-USD')

st.subheader(f'The current price of Bitcoin is ${bitPrice[1]:,.2f} extracted at {bitPrice[0].strftime("%Y-%b-%d %H:%M %Z")}')

tweetsData = get_bitcoin_price(tweets)
tweetsData = get_investment_value(tweetsData)

tweetsDf = dict_to_df(tweetsData)

tweetsHtml = format_df(tweetsDf.copy())
with st.container():
    st.write(tweetsHtml, unsafe_allow_html=True)

with st.container():
    port_return = portfolio_return(tweetsDf)
    st.text('')
    st.subheader(f'The government of Nayib Bukele has invested a total of ${port_return["totalCost"]:,.2f} of tax payer money in Bitcoin.')
    pt1 = f'These investments have an Unrealized {"Loss" if port_return["return"] < 0 else "Gain"} of'
    pt2 = f'{port_return["return"]:+,.2f} %'
    pt3 = f'$({abs(tweetsDf["gain/loss"].sum()):,.2f})' if (tweetsDf["gain/loss"].sum())<0 else f'${tweetsDf["gain/loss"].sum():.2f}'
    st.subheader(f'{pt1} {pt2} or {pt3}')

    st.text('* The calculations above exclude commission rates, transaction costs, and any other costs undisclosed by the governments.')
    st.text("* All of the information about Bitcoin purchases was extracted from Nayib Bukele's Twitter account")

with st.expander("Bitcoin Price Chart"):
    df = get_bitcoin_data('BTC-USD', dt.date.today() - dt.timedelta(days=365), dt.date.today(), None)

    fig = create_plot()
    line_chart(df, fig)
    fig.update_layout(
        title="Bitcoin Price Chart"
    )

    st.plotly_chart(fig, use_container_width=True)
