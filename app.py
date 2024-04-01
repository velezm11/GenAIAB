
import streamlit as st
import requests

# Define API endpoint
API_ENDPOINT = "https://3fj11w32na.execute-api.us-east-1.amazonaws.com/Prod/hello/"

# Streamlit app
def main():
st.set_page_config(page_title="AnyWhere AI Assistant", page_icon="Air Products Logo.png")
st.title("AnyWhere AI Assistant")

"""
Your Desk-side Digital Genius. Redefining Efficiency, One Prompt at a Time!
"""


    # Input field for user's prompt
    user_prompt = st.text_input("Enter your prompt")

    # Button to send POST request
    if st.button("Send Prompt"):
        try:
            # Send POST request to API with user's prompt
            response = requests.post(API_ENDPOINT, data=user_prompt)

            # Display response
            st.subheader("Response:")
            if response.status_code == 200:
                response_text = response.text
                st.write(response_text)
            else:
                st.error(f"Error {response.status_code}: {response.reason}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
