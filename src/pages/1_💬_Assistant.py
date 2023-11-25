"""Assistant"""
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain.utilities import SerpAPIWrapper
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI

load_dotenv()
NAME = os.getenv("NAME")
HEALTH_RECORD_FILE = os.getenv("HEALTH_RECORD_FILE")
HEALTH_WORKOUT_FILE = os.getenv("HEALTH_WORKOUT_FILE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

st.set_page_config(page_title="Assistant", page_icon="💬")
st.sidebar.header("Assistant")
st.sidebar.write(
    """
Personal Assistant
"""
)

MODEL_NAME = "gpt-3.5-turbo-0613"
# MODEL_NAME = "gpt-4-0613"

llm = ChatOpenAI(
    model_name=MODEL_NAME,
    openai_api_key=OPENAI_API_KEY,
    streaming=True,
    temperature=0,
)

tools = [
    Tool(
        name="Workout",
        func=create_csv_agent(
            llm,
            HEALTH_WORKOUT_FILE,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
        ).run,
        description="useful for when you need to answer questions about workout history.",
    ),
    Tool(
        name="Search",
        func=SerpAPIWrapper().run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    ),
]

if MODEL_NAME == "gpt-4-0613":
    assistant = initialize_agent(
        tools,
        llm,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True,
        max_iterations=3,
    )

if MODEL_NAME == "gpt-3.5-turbo-0613":
    assistant = create_csv_agent(
        llm,
        HEALTH_WORKOUT_FILE,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True,
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
    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
    response = assistant.run(prompt, callbacks=[st_cb])
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.write(response)
