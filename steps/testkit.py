import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START ,END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
load_dotenv()

# Ensure that the OPENAI_API_KEY environment variable is set
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Define your tools
def get_google_business_data(query: str) -> dict:
    """Simulates getting data from Google Business."""
    print("get_google_business_data called with query:", query)
    data = {
        "name": "Dummy Business",
        "phone": "+1-555-123-4567",
        "location": "123 Main St, Anytown, USA"
    }
    return data

def save_data(data: dict):
    """Placeholder function to save data."""
    print(f"Data saved: {data}")

# Bind the tools
llm = ChatOpenAI(model="gpt-4")  # Use "gpt-3.5-turbo" if needed
llm_with_tools = llm.bind_tools([get_google_business_data])

# System message
sys_msg = SystemMessage(content="""You are an assistant that helps users retrieve data from Google Business.

- Use the 'get_google_business_data' tool to retrieve data based on the user's query.
- After retrieving the data, display it to the user.
- Ask the user if they would like to save the data.
""")

def assistant(state: MessagesState):
    conversation = [sys_msg] + state["messages"]
    assistant_message = llm_with_tools.invoke(conversation)
    return {"messages": [assistant_message]}

def human_feedback(state: MessagesState):
    pass  # Placeholder for human feedback

def save_data_node(state: MessagesState):
    # Find the last 'tool' message, which should be from 'get_google_business_data'
    data = None
    for message in reversed(state["messages"]):
        if message.type == 'tool' and message.name == 'get_google_business_data':
            data = message.content  # Data returned by the tool
            break
    if data:
        save_data(data)
        response = AIMessage(content="Great! The data has been saved. Is there anything else I can assist you with?")
    else:
        response = AIMessage(content="I'm sorry, I couldn't find any data to save.")
    return {"messages": [response]}

def should_save_data(state: MessagesState):
    last_user_message = state["messages"][-1].content.lower()
    if 'yes' in last_user_message:
        return 'yes'
    else:
        return 'no'

# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode([get_google_business_data]))
builder.add_node("human_feedback", human_feedback)
builder.add_node("save_data_node", save_data_node)
builder.set_entry_point("assistant")
# Define the control flow edges

builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "human_feedback")

builder.add_conditional_edges(
    "human_feedback",
    should_save_data,
    {"yes": "save_data_node", "no": "assistant"}
)
builder.add_edge("save_data_node", "assistant")
builder.add_edge("human_feedback", "assistant")  # For 'no' response

# Set up a breakpoint before the 'human_feedback' node
memory = MemorySaver()
graph = builder.compile(interrupt_before=["human_feedback"], checkpointer=memory)
image = graph.get_graph(xray=True).draw_mermaid_png()
with open('output.png', 'wb') as f:
    f.write(image)
# Initialize thread
thread = {"configurable": {"thread_id": "1"}}

# Start the conversation loop
print("Type 'exit' or 'quit' to end the conversation.")
initial_input = {"messages": []}

while True:
  # We have reached a breakpoint at 'human_feedback'
    user_input = input("You: ")
    initial_input["messages"].append(user_input)
    if user_input.lower() in ["exit", "quit"]:
        print("Conversation ended.")
        break
    # Run the graph until the next interruption
    for event in graph.stream(initial_input, thread, stream_mode="values"):
        last_message = event["messages"][-1]
        if last_message.type == 'ai':
            print(f"Assistant: {last_message.content}")
        elif last_message.type == 'tool':
            # Optionally display tool messages
            pass
        elif last_message.type == 'human':
            # Breakpoint reached at 'human_feedback'
            break

    
    # Update the state with the user's response
    graph.update_state(thread, {"messages": [HumanMessage(content=user_input)]}, as_node="human_feedback")
