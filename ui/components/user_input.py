# components/user_input.py

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
                st.session_state.data_to_save = content
                # Parsear el contenido si es JSON
                try:
                    data_dict = json.loads(content)
                    df = pd.DataFrame(data_dict)
                    st.dataframe(df, use_container_width=True)
                except json.JSONDecodeError:
                    st.write(content)
            elif output_type == "final":
                message_placeholder.markdown(response_container["full_response"])
                st.session_state.conversation_history.append(
                    AIMessage(content=response_container["full_response"])
                )
            elif output_type == "save_prompt":
                st.session_state.show_save_prompt = True
