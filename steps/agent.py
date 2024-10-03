# agent.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
from tools import web_search

load_dotenv()


# Set up the OpenAI API key
# Ensure that the OPENAI_API_KEY environment variable is set
# Alternatively, you can set it here:
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Ensure that the OPENAI_API_KEY environment variable is set
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize the language model
llm = ChatOpenAI(model="gpt-4", streaming=True, openai_api_key=OPENAI_API_KEY)

# Bind the tools to the language model
tools = [web_search]
llm_with_tools = llm.bind_tools(tools)

# Define the system message
sys_msg = SystemMessage(content="You are a helpful assistant that can search the web using Tabily when needed.")

# Define the assistant node
def assistant(state: MessagesState):
    # Combine system message and conversation history
    messages = [sys_msg] + state["messages"]
    # Get the assistant's response
    response = llm_with_tools.invoke(messages)
    # Append the response to the messages
    return {"messages": [response]}

# Define the human feedback node
def human_feedback(state: MessagesState):
    # This node will be used to pause the graph for human input
    pass  # It's a placeholder

# Create the tool node
tool_node = ToolNode(tools)

# Build the graph
builder = StateGraph(MessagesState)

# Add nodes to the graph
builder.add_node("assistant", assistant)
builder.add_node("tools", tool_node)
builder.add_node("human_feedback", human_feedback)

# Define edges to determine the control flow
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "human_feedback")
builder.add_edge("human_feedback", "assistant")

# Initialize the in-memory checkpoint saver
memory = MemorySaver()

# Compile the graph with a breakpoint before 'human_feedback'
graph = builder.compile(checkpointer=memory, interrupt_before=["human_feedback"])

# Function to get the graph
def get_graph():
    return graph
