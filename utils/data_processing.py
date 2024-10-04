import json
from langchain_core.messages import HumanMessage, ToolMessage
from graph_agent.assistant_graph import create_assistant_graph

async def process_user_input(user_input, conversation_history, thread):
    graph = create_assistant_graph()
    state = {"messages": conversation_history + [HumanMessage(content=user_input)]}
    full_response = ""
    data_to_save = None
    tool_name = None  # Initialize tool_name

    async for event in graph.astream_events(state, thread, version="v2"):
        if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node', '') == 'assistant':
            chunk_content = event["data"]["chunk"].content
            full_response += chunk_content
            yield "stream", chunk_content
        elif event["event"] == "on_tool_end":
            tool_output = event['data']['output']
            
            # Check if tool_output is a ToolMessage instance
            if isinstance(tool_output, ToolMessage):
                tool_name = tool_output.name  # Extract tool_name from tool_output
                tool_output_content = tool_output.content
            else:
                tool_name = None
                tool_output_content = tool_output
            
            # Prepare data to save with tool_name
            data_to_save = {
                "tool_name": tool_name,
                "data": tool_output_content
            }

            yield "data", json.dumps(data_to_save)

    yield "final", full_response
    if data_to_save:
        yield "save_prompt", None
