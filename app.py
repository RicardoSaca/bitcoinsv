import streamlit as st
import pandas as pd
import datetime as dt
from functions import dict_to_df, get_bitcoin_data, get_bitcoin_price, get_investment_value, get_latest_bitcoin_price, format_df, df_to_html, portfolio_return, create_plot, line_chart, get_daily_bitcoin, add_daily
from tweets import tweets

st.set_page_config(layout="wide")

st.markdown("# 🇸🇻 El Salvador's Government Bitcoin Tracker")

#Get Bitcoin data
bitDaily =  get_bitcoin_data("BTC-USD", dt.datetime(2022, 11, 16), pd.Timestamp.today(), "Close", "1d")
#Set min and max date from tweets dictionary
minDate = tweets[min(tweets, key=lambda x:tweets[x]['date'])]['date'].replace(second=0, hour=0, minute=0)
maxDate = tweets[max(tweets, key=lambda x:tweets[x]['date'])]['date'].replace(second=0, hour=0, minute=0) + dt.timedelta(days=1)
bitHourly = get_bitcoin_data("BTC-USD", minDate, maxDate, "Close", "1h")

# Prep all data
bitPrice = get_latest_bitcoin_price('BTC-USD')
tweetsData = get_bitcoin_price(tweets, bitHourly) # get info for regular tweets
tweetsDaily = get_daily_bitcoin(tweets, bitDaily) # get daily purhcases
tweetsAll = {**tweetsData} # join Tweet dictionaries
tweetsAll.pop(12) # drop Tweet announcing daily purchases


#DAILY LOGIC
dailyComplete = get_investment_value(tweetsDaily, bitPrice[1])
dailyDf = dict_to_df(dailyComplete)
dailyFormat = format_df(dailyDf.copy())
dailyHtml = df_to_html(dailyFormat)
dailyRow = add_daily(dailyDf)

tweetsComplete = get_investment_value(tweetsAll, bitPrice[1])
tweetsComplete[(len(tweetsDaily)+1)] = dailyRow
tweetsDf = dict_to_df(tweetsComplete)
tweetsFormat = format_df(tweetsDf.copy(), summary=True)
portReturn = portfolio_return(tweetsFormat)
tweetsHtml = df_to_html(tweetsFormat)


col1, col2, col3 = st.columns(3)

with col1:
    #Investment Position Value
    st.metric(f"Bukele's Position", value=f"${portReturn['current']:,.2f}", delta=f"₿{tweetsDf['num_coins'].sum():,.0f}", delta_color='off')
with col2:
    #Investment Gain/Loss
    port_delta = f'$({abs(tweetsDf["gain/loss"].sum()):,.2f})' if (tweetsDf["gain/loss"].sum())<0 else f'${tweetsDf["gain/loss"].sum():.2f}'
    st.metric(f"Position Return", value=port_delta, delta=f"{portReturn['return']:-,.2f}%")
with col3:
    #Bitcoin Value
    time = pd.Timestamp(bitPrice[0], tz='UTC').tz_convert('America/El_Salvador')
    st.metric(f'Bitcoin Price as of {time.strftime("%Y-%b-%d %H:%M %Z")}', value=f'${bitPrice[1]:,.2f}')

with st.container():
    st.write(tweetsHtml, unsafe_allow_html=True)
    st.text('')


with st.expander("Daily Bitcoin Purchase Detail 🔁"):
    st.write(dailyHtml, unsafe_allow_html=True)

with st.container():
    st.text('')
    pt3 = f'$({abs(tweetsDf["gain/loss"].sum()):,.2f})' if (tweetsDf["gain/loss"].sum())<0 else f'${tweetsDf["gain/loss"].sum():.2f}'
    color = f"{'green' if portReturn['return'] > 0 else 'red'}"
    total_cost = f"{portReturn['totalCost']:,.2f}"
    st.markdown('# Summary:')
    st.markdown(
        f"""
            <span style='font-size:1.5em;'>Bukele has invested \${total_cost} of tax payer money in Bitcoin with an Unrealized {':chart_with_downwards_trend:' if portReturn['return'] < 0 else ':chart_with_upwards_trend:'} of <span style='color:{color};'>{portReturn['return']:+,.2f}% </span> or  <span style='color:{color};'>{pt3}</span></span>

            * The calculations above exclude commission rates, transaction costs, and any other costs undisclosed by the government.
            * All of the information about Bitcoin purchases was extracted from <a target="_blank" href='https://twitter.com/nayibbukele?s=20&t=VGMt2H2TdZ3pnnrEceTaKw' style="text-decoration:none;"> Nayib Bukele's Twitter account</a>.
            * The Bitcoin Price information was retrieved from yahoo finance, the price of purchase is calculated on the closest hour to the time of purchase.
            * The information is a close approximation, however it is recommended that the data is read with a pinch of salt.
            * Bukele announced via <a target="_blank" href="https://twitter.com/nayibbukele/status/1593113857261965312?s=46&t=lTdkuYKDUQ6KKCYNpKuVIQ" style="text-decoration:none;">Twitter on November 16th, 2022</a> that he would purchase one Bitcoin a day starting November 17th, 2022. Purchases are implemented using the daily close as the daily estimated purchase value.
        """
    , unsafe_allow_html=True)
    st.text('')

with st.expander("Bitcoin Price Chart"):
    df = get_bitcoin_data('BTC-USD', dt.date.today() - dt.timedelta(days=365), dt.date.today(), None, '1h')

    fig = create_plot()
    line_chart(df, fig)
    fig.update_layout(
        title="Bitcoin Price Chart"
    )

    st.plotly_chart(fig, use_container_width=True)