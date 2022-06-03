from collections import namedtuple
from genericpath import exists
import altair as alt
import math
import pandas as pd
import streamlit as st
import s3fs
from datetime import datetime, timedelta
import sys
import boto3

"""
# SANNE Files

Select the Date to view and also the File Type


"""
fs = s3fs.S3FileSystem(anon=False)

def read_file(filename):
    with fs.open(filename) as f:
        return f.read().decode("utf-8")

def get_transaction_data():
    days_to_subtract = 1
    d = st.date_input("Select Date to view", datetime.now() - timedelta(days=days_to_subtract))
    d_formatted = d.strftime("%Y%m%d")
    st.write('Selected Date is', d_formatted) 
    option = st.selectbox(
     label='Which file do you want to view?',
     options=('PortfolioValuationAndHolding', 'CashAccount', 'IncomeData', 'Transactions'), index=0)
    st.write('You selected:', option)
    #AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    AWS_S3_BUCKET = "sanne-eod"
    key = option+"_"+d_formatted+"_SLTWWF.csv"
    st.write('File Key', key) 
    #content = read_file("sanne-eod/CashAccount_20220413_SLTWWF.csv")
    try:
        df = pd.read_csv(f"s3://{AWS_S3_BUCKET}/{key}",)
        df = df.set_index("InstrumentCode")
        #countries = st.multiselect(
        #"Choose countries", list(df.index), ["ZAR", "SLFA1"]
        #)
        data = df 
        st.dataframe(data, width=1200)
        #if not countries:
        #    st.error("Please select at least one account.")
        #else:
            #data = df.loc[countries]
            
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
            **Some error occured**
            Detail: %s
        """
            % str(e)
            )
        return "ERROR"

def get_list_of_files():


    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('option.eod')

    for object_summary in my_bucket.objects.filter(Prefix="2022-06-03/"):
        file_list = print(object_summary.key)
    st.table(file_list)



output = get_transaction_data()
output2 =  get_list_of_files()
