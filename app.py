from operator import index
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from functions import dict_to_df, get_bitcoin_data, get_bitcoin_price, get_investment_value, get_latest_bitcoin_price, format_df, portfolio_return, create_plot, line_chart, get_daily_bitcoin
from tweets import tweets

st.set_page_config(layout="wide")

st.markdown("# :flag-sv: El Salvador's Government Bitcoin Tracker")

# Prep all data
bitPrice = get_latest_bitcoin_price('BTC-USD')
tweetsData = get_bitcoin_price(tweets)
tweetsData = get_daily_bitcoin(tweetsData)
tweetsData = get_investment_value(tweetsData)
tweetsDf = dict_to_df(tweetsData)
port_return = portfolio_return(tweetsDf)
tweetsHtml = format_df(tweetsDf.copy())

col1, col2, col3 = st.columns(3)

with col1:
    #Investment Position Value
    st.metric(f"Buekele's Position", value=f"${port_return['current']:,.2f}", delta=f"₿{tweetsDf['num_coins'].sum():,.0f}", delta_color='off')
with col2:
    #Investment Gain/Loss
    port_delta = f'$({abs(tweetsDf["gain/loss"].sum()):,.2f})' if (tweetsDf["gain/loss"].sum())<0 else f'${tweetsDf["gain/loss"].sum():.2f}'
    st.metric(f"Postion Return", value=port_delta, delta=f"{port_return['return']:-,.2f}%")
with col3:
    #Bitcoin Value
    st.metric(f'Bitcoin Price as of {bitPrice[0].strftime("%Y-%b-%d %H:%M %Z")}', value=f'${bitPrice[1]:,.2f}')

with st.container():
    st.write(tweetsHtml, unsafe_allow_html=True)

with st.container():
    st.text('')
    # pt1 = f'These investments have an Unrealized {"Loss" if port_return["return"] < 0 else "Gain"} of'
    # pt2 = f'{port_return["return"]:+,.2f} %'
    pt3 = f'$({abs(tweetsDf["gain/loss"].sum()):,.2f})' if (tweetsDf["gain/loss"].sum())<0 else f'${tweetsDf["gain/loss"].sum():.2f}'
    color = f"{'green' if port_return['return'] > 0 else 'red'}"
    total_cost = f"{port_return['totalCost']:,.2f}"
    st.markdown('# Summary:')
    # ${port_return['totalCost']:,.2f}
    st.markdown(
        f"""
            <span style='font-size:1.5em;'>Bukele has invested \${total_cost} of tax payer money in Bitcoin with an Unrealized {':chart_with_downwards_trend:' if port_return['return'] < 0 else ':chart_with_upwards_trend:'} of <span style='color:{color};'>{port_return['return']:+,.2f}% </span> or  <span style='color:{color};'>{pt3}</span></span>

            * The calculations above exclude commission rates, transaction costs, and any other costs undisclosed by the government.
            * All of the information about Bitcoin purchases was extracted from <a target="_blank" href='https://twitter.com/nayibbukele?s=20&t=VGMt2H2TdZ3pnnrEceTaKw' style="text-decoration:none;"> Nayib Bukele's Twitter account</a>.
            * The Bitcoin Price information was retrieved from yahoo finance, the price of purchase is calculated on the closest hour to the time of purchase.
            * The information is a close approximation, however it is recommended that the data is read with a pinch of salt.
            * Bukele announced via <a target="_blank" href="https://twitter.com/nayibbukele/status/1593113857261965312?s=46&t=lTdkuYKDUQ6KKCYNpKuVIQ" style="text-decoration:none;">Twitter on November 16th, 2022</a> that he would purchase one Bitcoin a day starting November 17th, 2022.
        """
    , unsafe_allow_html=True)
    st.text('')
    # st.subheader(f'The government of Nayib Bukele has invested a total of ${port_return["totalCost"]:,.2f} of tax payer money in Bitcoin.')
    # st.subheader(f'{pt1} {pt2} or {pt3}')

with st.expander("Bitcoin Price Chart"):
    df = get_bitcoin_data('BTC-USD', dt.date.today() - dt.timedelta(days=365), dt.date.today(), None, '1h')

    fig = create_plot()
    line_chart(df, fig)
    fig.update_layout(
        title="Bitcoin Price Chart"
    )

    st.plotly_chart(fig, use_container_width=True)
