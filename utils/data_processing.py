# utils/data_processing.py

import json
from langchain_core.messages import HumanMessage, ToolMessage
from graph_agent.assistant_graph import create_assistant_graph

async def process_user_input(user_input, conversation_history, thread):
    graph = create_assistant_graph()
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
            
            # Extraer contenido si es ToolMessage
            if isinstance(tool_output, ToolMessage):
                tool_output_content = tool_output.content
            else:
                tool_output_content = tool_output
            
            # Convertir a JSON si es necesario
            if isinstance(tool_output_content, dict):
                data_to_save = json.dumps(tool_output_content)
            elif isinstance(tool_output_content, str):
                data_to_save = tool_output_content
            else:
                data_to_save = json.dumps({"data": str(tool_output_content)})
            
            yield "data", data_to_save

    yield "final", full_response
    if data_to_save:
        yield "save_prompt", None
