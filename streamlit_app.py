from collections import namedtuple
from genericpath import exists
import altair as alt
import math
import pandas as pd
import streamlit as st
import s3fs
from datetime import datetime, timedelta
import sys


"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""
fs = s3fs.S3FileSystem(anon=False)

def read_file(filename):
    with fs.open(filename) as f:
        return f.read().decode("utf-8")

def get_UN_data():
    days_to_subtract = 1
    d = st.date_input("Select Date to view", datetime.now() - timedelta(days=days_to_subtract))
    d_formatted = d.strftime("%Y%m%d")
    st.write('Selected Date is', d_formatted) 
    #AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    AWS_S3_BUCKET = "sanne-eod"
    key = "CashAccount_"+d_formatted+"_SLTWWF.csv"
    #content = read_file("sanne-eod/CashAccount_20220413_SLTWWF.csv")
    try:
        df = pd.read_csv(f"s3://{AWS_S3_BUCKET}/{key}",)
        df = df.set_index("InstrumentCode")
        countries = st.multiselect(
        "Choose countries", list(df.index), ["ZAR", "SLFA1"]
        )
        if not countries:
            st.error("Please select at least one account.")
        else:
            data = df.loc[countries]
            st.table(data)
            #data /= 1000000.0
            #st.write("### Gross Agricultural Production ($B)", data.sort_index())

            # data = data.T.reset_index()
            # data = pd.melt(data, id_vars=["index"]).rename(
            #     columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
            # )
            # chart = (
            #     alt.Chart(data)
            #     .mark_area(opacity=0.3)
            #     .encode(
            #         x="year:T",
            #         y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
            #         color="Region:N",
            #     )
            # )
            # st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % str(e + key)
            )
        return "ERROR"


output = get_UN_data()
