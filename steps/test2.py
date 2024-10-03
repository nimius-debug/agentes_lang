import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()
# Ensure OpenAI API key is set
if 'OPENAI_API_KEY' not in os.environ:
    os.environ['OPENAI_API_KEY'] = input("Enter your OpenAI API Key: ")

# Define your tools
def get_google_business_data(query: str) -> dict:
    """Simulates getting data from Google Business."""
    print("get_google_business_data called with query:", query)
    data = {
        "name": f"Business {query}",
        "phone": "+1-555-123-4567",
        "location": f"123 {query} St, Anytown, USA"
    }
    return data

def save_data(data: dict):
    """Simulates saving data."""
    print(f"Data saved: {data}")

# Bind the tools
tools = [get_google_business_data, save_data]
llm = ChatOpenAI(model="gpt-4")  # Use "gpt-3.5-turbo" if needed
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content="""You are an assistant that helps users retrieve data from Google Business.

- Use the 'get_google_business_data' tool to retrieve data based on the user's query.
- After retrieving the data, display it to the user.
- Ask the user if they would like to save the data.
- If the user says 'yes', use the 'save_data' tool to save the data.
- If the user says 'no', politely acknowledge and continue the conversation.
""")

def assistant(state):
    conversation = [sys_msg] + state["messages"]
    assistant_message = llm_with_tools.invoke(conversation)
    return {"messages": [assistant_message]}

def human_feedback(state):
    pass  # Placeholder for human feedback

# Build the graph
builder = StateGraph()
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("human_feedback", human_feedback)

# Define the control flow edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "human_feedback")
builder.add_edge("human_feedback", "assistant")  # Loop back to assistant after user input

# Set up a breakpoint after the 'tools' node
memory = MemorySaver()
graph = builder.compile(interrupt_after=["tools"], checkpointer=memory)

# Initialize thread
thread = {"configurable": {"thread_id": "1"}}

# Provide initial input to start the assistant
initial_input = {"messages": []}

# Run the graph the first time to get the assistant's initial message
for event in graph.stream(initial_input, thread, stream_mode="values"):
    last_message = event["messages"][-1]
    if last_message.type == 'ai':
        print(f"Assistant: {last_message.content}")
    elif last_message.type == 'tool':
        pass
    elif last_message.type == 'human':
        break  # Breakpoint reached

print("Type 'exit' or 'quit' to end the conversation.")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Conversation ended.")
        break

    # Update the state with the user's message
    graph.update_state(thread, {"messages": [HumanMessage(content=user_input)]}, as_node="assistant")

    # Run the graph until the next interruption
    interrupted = False
    for event in graph.stream(None, thread, stream_mode="values"):
        last_message = event["messages"][-1]
        if last_message.type == 'ai':
            print(f"Assistant: {last_message.content}")
        elif last_message.type == 'tool':
            pass
        elif last_message.type == 'human':
            interrupted = True
            break  # Breakpoint reached after 'tools'

    if interrupted:
        # At this point, the 'tools' node has been executed, and we need to get user feedback
        # The assistant has already asked if the user wants to save the data
        # Get the user's response
        user_decision = input("You: ")
        if user_decision.lower() in ["exit", "quit"]:
            print("Conversation ended.")
            break

        # Update the state with the user's response at 'human_feedback' node
        graph.update_state(thread, {"messages": [HumanMessage(content=user_decision)]}, as_node="human_feedback")

        # Continue the graph execution
        for event in graph.stream(None, thread, stream_mode="values"):
            last_message = event["messages"][-1]
            if last_message.type == 'ai':
                print(f"Assistant: {last_message.content}")
            elif last_message.type == 'tool':
                pass
            elif last_message.type == 'human':
                break  # Breakpoint (if any)
