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
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
load_dotenv()

# Ensure that the OPENAI_API_KEY environment variable is set
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
  
# Set up models
models = {
    "gpt-4": ChatOpenAI(model="gpt-4", temperature=0.5, streaming=True),
}  
# Define your tools
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

# List of tools
tools = [get_google_business_data ]
# Define the assistant's instructions
current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
You are an assistant that helps users retrieve data from Google Business.

- Use the 'get_google_business_data' tool to retrieve data based on the user's query.
- After retrieving the data, display it to the user.
- Ask the user if they would like to save the data.
- If the user says 'yes', use the 'save_data' tool to save the data.
- If the user says 'no', politely acknowledge and continue the conversation.
- Today's date is {current_date}.
"""

# Define the AgentState
class AgentState(MessagesState):
    pass  # No additional state required

# Wrap the model to include the system instructions and bind tools
def wrap_model(model: BaseChatModel):
    model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | model
def human_feedback(state: AgentState):
    pass  # Placeholder for human feedback

def save_data_node(state: AgentState):
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
      
# Define the assistant's main function
async def acall_model(state: AgentState, config: RunnableConfig):
    m = models[config["configurable"].get("model", "gpt-4")]
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    # We return a list because this will get added to the existing list
    return {"messages": [response]}

# Define the graph
agent = StateGraph(AgentState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.add_node("human_feedback", human_feedback)
agent.add_node("save_data_node", save_data_node)
agent.set_entry_point("model")

# Always run "model" after "tools"
agent.add_edge("tools", "model")
agent.add_conditional_edges(
    "model",
    tools_condition,
)
agent.add_edge("tools", "human_feedback")
agent.add_conditional_edges(
    "human_feedback",
    should_save_data,
    {"yes": "save_data_node", "no": "model"}
)
# After "model", if there are tool calls, run "tools". Otherwise END.
def pending_tool_calls(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    else:
        return "done"

agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})


# Compile the agent
assistant_agent = agent.compile(checkpointer=MemorySaver(),)

image = assistant_agent.get_graph(xray=True).draw_mermaid_png()
with open('outp.png', 'wb') as f:
    f.write(image)

# Conversation loop
async def conversation_loop():
    # Initialize thread
    thread_id = str(uuid4())
    thread = {"configurable": {"thread_id": thread_id}}

    # Initial state
    state = {"messages": []}

    print("Type 'exit' or 'quit' to end the conversation.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Conversation ended.")
            break

        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))

        # Run the assistant
        result = await assistant_agent.ainvoke(
            state,
            config=RunnableConfig(configurable={"thread_id": thread_id}),
        )

        # Update state with assistant's response
        state["messages"].extend(result["messages"])

        # Print assistant's response
        last_message = result["messages"][-1]
        print(f"Assistant: {last_message.content}")

# Entry point
if __name__ == "__main__":
    # Run the conversation loop
    asyncio.run(conversation_loop())
