from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

import streamlit as st
import requests

st.set_page_config(page_title="Hybrid Search AI Assistant", page_icon="peccy.png")
st.title("Hybrid Search AI Assistant")

"""
Your Desk-side Digital Genius. Redefining Efficiency, One Prompt at a Time!
"""

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")



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
    api_endpoint = "https://7nk9sh7271.execute-api.us-west-2.amazonaws.com/Prod/hello/"
    payload = {"question": query}
    response = requests.post(api_endpoint, json=payload)
    return response.json()

chain_with_history = RunnableWithMessageHistory(
    prompt,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    response = send_query_to_api(prompt)
    st.chat_message("ai").write(response)


