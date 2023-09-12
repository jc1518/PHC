"""Assistant"""
import os
from dotenv import load_dotenv

import streamlit as st
import pandas as pd
from langchain.agents import AgentType, create_csv_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI


load_dotenv()
NAME = os.getenv("NAME")
HEALTH_RECORD_FILE = os.getenv("HEALTH_RECORD_FILE")
HEALTH_WORKOUT_FILE = os.getenv("HEALTH_WORKOUT_FILE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Assistant", page_icon="💬")
st.sidebar.header("Assistant")
st.sidebar.write(
    """
Personal Assistant
"""
)

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo-0613",
    openai_api_key=OPENAI_API_KEY,
    streaming=True,
    temperature=0,
)

workout_agent = create_csv_agent(
    llm,
    HEALTH_WORKOUT_FILE,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": f"Hi {NAME}! I hope you're having a great day. How can I help you?",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input(placeholder=""):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
    response = workout_agent.run(prompt, callbacks=[st_cb])
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.write(response)
