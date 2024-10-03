from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.runnables import RunnableConfig
from config import SYSTEM_MESSAGE
from tools.google_business import get_google_business_data
from langchain_community.tools.tavily_search import TavilySearchResults

def create_assistant_graph():
    tavily_tool = TavilySearchResults(max_results=5)
    tools = [get_google_business_data, tavily_tool]
    llm = ChatOpenAI(model="gpt-4", streaming=True)
    llm_with_tools = llm.bind_tools(tools)

    sys_msg = SystemMessage(content=SYSTEM_MESSAGE)

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

    return graph

