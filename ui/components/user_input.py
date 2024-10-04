import asyncio
import json
import pandas as pd
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from utils.data_processing import process_user_input

async def handle_user_input(user_input):
    st.session_state.conversation_history.append(HumanMessage(content=user_input))
    with st.chat_message("user", avatar="🧑‍💻"):
        st.write(user_input)

    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        response_container = {"full_response": ""}

        async for output_type, content in process_user_input(
            user_input, st.session_state.conversation_history, st.session_state.thread
        ):
            if output_type == "stream":
                response_container["full_response"] += content
                message_placeholder.markdown(response_container["full_response"] + "▌")
            elif output_type == "data":
                print(f"Data received: {content}")
                # Parse the content as JSON
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as e:
                    st.write(f"Error parsing data: {e}")
                    data = {}

                tool_name = data.get("tool_name")
                print(f"Tool name: {tool_name}")

                if tool_name == "get_google_business_data":
                    st.session_state.data_to_save = data['data']
                    # Ensure data is a list of dictionaries
                    if isinstance(data['data'], str):
                        # If data is a string, parse it as JSON
                        try:
                            data_list = json.loads(data['data'])
                        except json.JSONDecodeError as e:
                            st.write(f"Error parsing data['data']: {e}")
                            data_list = []
                    elif isinstance(data['data'], list):
                        data_list = data['data']
                    else:
                        data_list = []

                    if data_list:
                        df = pd.DataFrame(data_list)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write("Received data is not in the expected format.")
                        
                elif tool_name == "tavily_search_results_json":
                    # Parse the data
                    try:
                        data_list = json.loads(data['data'])
                    except json.JSONDecodeError as e:
                        st.write(f"Error parsing data['data']: {e}")
                        data_list = []

                    if data_list:
                        # Generate markdown content
                        markdown_content = ""
                        for item in data_list:
                            url = item.get('url', 'No URL')
                            content_snippet = item.get('content', 'No content')
                            markdown_content += f"### [{url}]({url})\n\n{content_snippet}\n\n---\n"

                        # Display the markdown
                        st.markdown(markdown_content)
                    else:
                        st.write("Received data is not in the expected format.")
                else:
                    st.write(f"Data received is from an unknown tool: {tool_name}")
            elif output_type == "final":
                message_placeholder.markdown(response_container["full_response"])
                st.session_state.conversation_history.append(
                    AIMessage(content=response_container["full_response"])
                )
            elif output_type == "save_prompt":
                st.session_state.show_save_prompt = True
