import streamlit as st
import requests

if st.button('Trigger Lambda'):
    api_url = 'https://7nk9sh7271.execute-api.us-west-2.amazonaws.com/Prod/hello/'
    response = requests.post(api_url, json={'key':'value'})  # replace with your actual payload
    if response.status_code == 200:
        st.write("AWS Lambda function triggered successfully!")
    else:
        st.write(f"Failed to trigger AWS Lambda function. Status code: {response.status_code}")

