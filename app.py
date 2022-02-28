import streamlit as st
import pandas as pd
import numpy as np
from functions import get_bitcoin_price
from tweets import tweets

st.title("Inversion del Gobierno de El Salvado en Bitcoin")

for key in tweets:
    tweets[key]