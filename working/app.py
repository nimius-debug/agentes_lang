import os
import pandas as pd
import json
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
import asyncio
from uuid import uuid4
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.runnables import RunnableConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Tool definitions
def get_google_business_data(query: str) -> dict:
    """Simulates getting data from Google Business."""
    logging.info(f"get_google_business_data called with query: {query}")
    return {
        "name": "Dummy Business",
        "phone": "+1-555-123-4567",
        "location": "123 Main St, Anytown, USA"
    }

def save_data(data: str) -> str:
    """Simulates saving data."""
    logging.info(f"Attempting to save data: {data}")
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logging.error("Failed to parse data as JSON")
            return "Error: Invalid data format"
    # Simulate actual data saving process here
    result = "Data has been saved."
    logging.info(result)
    return result

# LLM and graph setup
tools = [get_google_business_data]
llm = ChatOpenAI(model="gpt-4", streaming=True)
llm_with_tools = llm.bind_tools(tools)

current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
You are an assistant that helps users retrieve data from Google Business.
- Use the 'get_google_business_data' tool to retrieve data based on the user's query.
- After retrieving the data, display it to the user.
- Do not ask the user if they want to save the data.
- Today's date is {current_date}.
"""
sys_msg = SystemMessage(content=instructions)

def assistant(state: MessagesState, config: RunnableConfig):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"], config=config)]}

builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Async function to process user input
async def process_user_input(user_input, conversation_history, thread):
    state = {"messages": conversation_history + [HumanMessage(content=user_input)]}
    full_response = ""
    data_to_save = None

    async for event in graph.astream_events(state, thread, version="v2"):
        if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node', '') == 'assistant':
            chunk_content = event["data"]["chunk"].content
            full_response += chunk_content
            yield "stream", chunk_content
        elif event["event"] == "on_tool_end":
            tool_output = event['data']['output']
            data_to_save = json.dumps(tool_output) if isinstance(tool_output, dict) else tool_output
            logging.info(f"Set data_to_save: {data_to_save}")
            yield "data", data_to_save

    yield "final", full_response
    if data_to_save:
        yield "save_prompt", None

# Streamlit UI setup
st.title("Assistant with Tool Integration")

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'thread' not in st.session_state:
    st.session_state.thread = {"configurable": {"thread_id": "1"}}
if 'data_to_save' not in st.session_state:
    st.session_state.data_to_save = None

# Display conversation history
for message in st.session_state.conversation_history:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.write(message.content)

# User input handling
user_input = st.chat_input("Type your message")

if user_input:
    st.session_state.conversation_history.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response_container = {"full_response": ""}

        # Create and run the async task
        async def run_conversation():
            async for output_type, content in process_user_input(user_input, st.session_state.conversation_history, st.session_state.thread):
                if output_type == "stream":
                    response_container["full_response"] += content
                    message_placeholder.markdown(response_container["full_response"] + "▌")
                elif output_type == "data":
                    st.session_state.data_to_save = content.content
                    # Parse JSON string to dictionary
                    data_dict = json.loads(content.content)
                    df = pd.DataFrame([data_dict])
                    st.dataframe(df, use_container_width=True)
                  
                    # st.dataframe(json.loads(content))
                elif output_type == "final":
                    message_placeholder.markdown(response_container["full_response"])
                    st.session_state.conversation_history.append(AIMessage(content=response_container["full_response"]))
                elif output_type == "save_prompt":
                    st.session_state.show_save_prompt = True

        # Run the async task
        asyncio.run(run_conversation())

# Save data prompt
if st.session_state.get('show_save_prompt', False) and st.session_state.data_to_save:
    st.markdown("#### Do you want to save the data?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes", key="save_button"):
            save_message = save_data(st.session_state.data_to_save)
            st.success(save_message)
            st.session_state.data_to_save = None
            st.session_state.show_save_prompt = False
    with col2:
        if st.button("No", key="no_save_button"):
            st.session_state.data_to_save = None
            st.session_state.show_save_prompt = False

# Debug information
if st.checkbox("Show debug info"):
    st.write("Debug Information:")
    st.write(f"data_to_save: {st.session_state.data_to_save}")
    st.write(f"conversation_history: {st.session_state.conversation_history}")