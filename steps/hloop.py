import os
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START,END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
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

def save_data(data: dict):
    """Placeholder function to save data."""
    print(f"Data saved: {data}")

tools = [get_google_business_data]
llm = ChatOpenAI(model="gpt-4o", streaming=True)
llm_with_tools = llm.bind_tools(tools)

# System message
current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
You are an assistant that helps users retrieve data from Google Business.

- Use the 'get_google_business_data' tool to retrieve data based on the user's query.
- After retrieving the data, display it to the user.
- Today's date is {current_date}.
"""
sys_msg = SystemMessage(content=instructions)

# Node
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine the control flow
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(interrupt_after=["tools"], checkpointer=memory)
image = graph.get_graph(xray=True).draw_mermaid_png()
with open('out12.png', 'wb') as f:
    f.write(image)

conversation_history = []
# Thread
thread = {"configurable": {"thread_id": "1"}}

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        print("Assistant: Goodbye!")
        break
    conversation_history.append(HumanMessage(content=user_input))
    state = {"messages": conversation_history}
    
    # Run the graph
    for event in graph.stream(state, thread, stream_mode="values"):
        print("**************************")
        # print(event)
        # print("**************************")
        assistant_reply = event['messages'][-1]
        assistant_reply.pretty_print()
        conversation_history.append(assistant_reply)
    
    