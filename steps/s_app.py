import os
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

load_dotenv()

# Ensure that the OPENAI_API_KEY environment variable is set
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Define the tools
def get_google_business_data(query: str) -> dict:
    """Simulates getting data from Google Business."""
    print("get_google_business_data called with query:", query)
    return {
        "name": "Dummy Business",
        "phone": "+1-555-123-4567",
        "location": "123 Main St, Anytown, USA"
    }

def save_data(data: dict) -> str:
    """Simulates saving data."""
    print(f"Data saved: {data}")
    return "Data has been saved."

# Only include get_google_business_data in the tools
tools = [get_google_business_data]
llm = ChatOpenAI(model="gpt-4", streaming=True)
llm_with_tools = llm.bind_tools(tools)

# System message
current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
You are an assistant that helps users retrieve data from Google Business.

- Use the 'get_google_business_data' tool to retrieve data based on the user's query.
- After retrieving the data, display it to the user.
- Do not ask the user if they want to save the data.
- Today's date is {current_date}.
"""
sys_msg = SystemMessage(content=instructions)

# Define the assistant node
def assistant(state: MessagesState, config: RunnableConfig):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"], config=config)]}

# Build the graph
builder = StateGraph(MessagesState)

# Define nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Set up the Streamlit app
st.title("Assistant with Tool Integration")

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'thread' not in st.session_state:
    st.session_state.thread = {"configurable": {"thread_id": "1"}}

if 'data_to_save' not in st.session_state:
    st.session_state.data_to_save = None

# Display the conversation
for message in st.session_state.conversation_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)


async def handle_user_input(user_input):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes"):
                print("YESSSSS...")
                # Call save_data function directly
               
    with col2:
        if st.button("No"):
            print("NOOOOOO...")
                
    # Display user's message immediately
    st.session_state.conversation_history.append(HumanMessage(content=user_input))
    with st.chat_message('user'):
        st.write(user_input)

    state = {"messages": st.session_state.conversation_history}
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Run the graph
        async for event in graph.astream_events(state, st.session_state.thread, version="v2"):
    
            if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node', '') == 'assistant':
                data = event["data"]
                chunk_content = data["chunk"].content
                full_response += chunk_content
                # Update the placeholder with the new content
                message_placeholder.markdown(full_response + "▌")
            elif event["event"] == "on_tool_end":
                
                tool_output = event['data']['output']
                
                st.session_state.data_to_save = tool_output
             
        message_placeholder.markdown(full_response)
        # Append the assistant's full response to the conversation history
        st.session_state.conversation_history.append(AIMessage(content=full_response))

    # After the assistant displays the data, check if data is available to save
    print("Data to save:", st.session_state.data_to_save)
    if st.session_state.data_to_save:
        st.markdown("#### Do you want to save the data?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes"):
                print("YESSSSS...")
                # Call save_data function directly
                save_message = save_data(st.session_state.data_to_save)
                print(save_message)
                st.success(save_message)
                st.session_state.data_to_save = None  # Reset the data_to_save
        with col2:
            if st.button("No"):
                print("NOOOOOO...")
                st.session_state.data_to_save = None  # Reset the data_to_save

# Check for user input and handle it
if user_input := st.chat_input("Type your message"):
    asyncio.run(handle_user_input(user_input))
