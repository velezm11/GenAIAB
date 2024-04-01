from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

import streamlit as st
import requests

st.set_page_config(page_title="AnyWhere AI Assistant", page_icon="Air Products Logo.png")
st.title("AnyWhere AI Assistant")

"""
Your Desk-side Digital Genius. Redefining Efficiency, One Prompt at a Time!
"""

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")


view_messages = st.expander("View the message contents in session state")
if "langchain_messages" not in st.session_state:
  st.session_state["langchain_messages"] = []

# Set up the LangChain, passing in Message History

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# Function to send user query to API Gateway and fetch response
def send_query_to_api(query):
    api_endpoint = "https://3fj11w32na.execute-api.us-east-1.amazonaws.com/Prod/hello/"
    payload = {"question": query}
    response = requests.post(api_endpoint, json=payload)
    return response.json()
