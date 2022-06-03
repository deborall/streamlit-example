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
import json
import plotly.express as px


"""
# Option Files

Select the Date to view and also the File Type


"""
fs = s3fs.S3FileSystem(anon=False)
#AWS_S3_BUCKET = "sanne-eod"
AWS_S3_BUCKET = "options.eod"


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

@st.cache()

def get_list_of_files():
    

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('options.eod')
    file_list = []
    for object_summary in my_bucket.objects.filter(Prefix=""):
        file_list.append(object_summary.key)
    

    return file_list


def read_file(filename):
    file_ref = AWS_S3_BUCKET + "/" + filename
    with fs.open(file_ref) as f:
        return f.read().decode("utf-8")

def load_data(key):
    #with open('TME.US.json') as data_file:    
    #    data = json.load(data_file)

    raw_data = read_file(key) 
    data = json.loads(raw_data)
    #st.text(data)
    
    #options_data = pd.json_normalize(data['data'][0]['options'][option_type])
    options_df = None
    options_list = data['data']

    for expiry_item in options_list:
        KEY_ERROR = "NO_TIGGER"
        try:
            call_items = pd.json_normalize(expiry_item['options']['CALL'])
        except KeyError as e:
            KEY_ERROR = "CALL_ERROR_TRIGGERED"
            continue
        
        try:
            put_items = pd.json_normalize(expiry_item['options']['PUT'])
        except KeyError as e:
            KEY_ERROR = "PUT_ERROR_TRIGGERED"
            continue

        if KEY_ERROR == "NO_TRIGGER":
            combined_df = pd.concat([call_items, put_items])
        elif KEY_ERROR == "CALL_ERROR_TRIGGERED":
            combined_df = put_items
        elif KEY_ERROR == "PUT_ERROR_TRIGGERED":
            combined_df = call_items
        else: 
            combined_df = pd.concat([call_items, put_items])
        if options_df is None:
          options_df = combined_df
        else:
          options_df = pd.concat([options_df, combined_df])

        
    #options_data = pd.json_normalize()
    return options_df




#output = get_transaction_data()

file_list =  get_list_of_files()
file_selected = st.selectbox("Select the file that you want", sorted(file_list,reverse=True))
option_type = st.selectbox("Type", ['CALL', 'PUT'], 0)
options_data = load_data(file_selected)
#st.text(options_data)
expiration_selected = st.selectbox(label="Expiry Date", options=options_data['expirationDate'].unique(), index=0)
selectedData = options_data[(options_data['expirationDate'] == expiration_selected) & (options_data['impliedVolatility'] > 0) & (options_data['type'] == option_type)]


#st.altair_chart(selectedData[['strike', 'impliedVolatility']], use_container_width=True)
fig = px.scatter(selectedData[['strike','impliedVolatility']], x="strike", y="impliedVolatility")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(selectedData)



