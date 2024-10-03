# app.py

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from agent import get_graph
import time

def main():
    st.set_page_config(page_title="LangGraph Agent with Tabily Search", page_icon="🔍")
    st.title("LangGraph Agent with Tabily Search 🔍")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.thread_id = "1"  # Initialize thread ID
        st.session_state.awaiting_human_feedback = False  # Flag for human feedback
        st.session_state.thread = None    # Initialize thread

    # Get the compiled graph
    graph = get_graph()

    # Display previous messages
    for message in st.session_state.messages:
        if message['role'] == 'user':
            with st.chat_message('user'):
                st.write(message['content'])
        else:
            with st.chat_message('assistant'):
                st.write(message['content'])

    if st.session_state.awaiting_human_feedback:
        # The graph is at the human_feedback node, awaiting user input
        st.write("The assistant is awaiting your feedback.")
        user_feedback = st.text_input("Provide feedback or corrections, or press Enter to continue:")

        if st.button("Submit Feedback") or user_feedback != "":
            if user_feedback != "":
                # Display user's feedback immediately
                with st.chat_message('user'):
                    st.write(user_feedback)
                st.session_state.messages.append({'role': 'user', 'content': user_feedback})

                # Update the state with the user's feedback
                graph.update_state(
                    st.session_state.thread,
                    {"messages": [HumanMessage(content=user_feedback)]},
                    as_node="human_feedback"
                )
            else:
                # Proceed without additional feedback
                graph.update_state(st.session_state.thread, {}, as_node="human_feedback")

            # Continue the graph execution and stream the assistant's response
            assistant_response = ""
            with st.chat_message('assistant'):
                response_placeholder = st.empty()

                # Define the callback function for token-wise streaming
                def on_llm_new_token(token: str):
                    nonlocal assistant_response
                    assistant_response += token
                    response_placeholder.markdown(assistant_response + "▌")

                # Create the RunnableConfig with the callback
                runnable_config = RunnableConfig(callbacks=[on_llm_new_token])

                # Run the graph with the node_configs
                for _ in graph.stream(
                    None,
                    st.session_state.thread,
                    node_configs={'assistant': {'config': runnable_config}}
                ):
                    pass  # The callback handles streaming

                response_placeholder.markdown(assistant_response)  # Remove the cursor
                st.session_state.messages.append({'role': 'assistant', 'content': assistant_response})

            # Reset the flag
            st.session_state.awaiting_human_feedback = False

    else:
        # User input
        if prompt := st.chat_input("Type your message"):
            # Display user's message immediately
            with st.chat_message('user'):
                st.write(prompt)
            st.session_state.messages.append({'role': 'user', 'content': prompt})

            # Create initial input for the graph
            initial_input = {"messages": [HumanMessage(content=prompt)]}

            # Thread configuration
            thread_id = st.session_state.thread_id
            thread = {"configurable": {"thread_id": thread_id}}
            st.session_state.thread = thread  # Save thread in session state

            # Define the callback function for token-wise streaming
            assistant_response = ""
            with st.chat_message('assistant'):
                response_placeholder = st.empty()

                def on_llm_new_token(token: str):
                    nonlocal assistant_response
                    assistant_response += token
                    response_placeholder.markdown(assistant_response + "▌")

                # Create the RunnableConfig with the callback
                runnable_config = RunnableConfig(callbacks=[on_llm_new_token])

                # Run the graph with the node_configs
                for chunck in graph.stream(
                    initial_input,
                    config={
                      'assistant': {
                        'config': runnable_config
                        },
                      "configurable": {
                        "thread_id": thread_id
                        }
                      }
                ):
                    print(chunck)

                response_placeholder.markdown(assistant_response)  # Remove the cursor
                st.session_state.messages.append({'role': 'assistant', 'content': assistant_response})

            # Check if the graph is waiting at the human_feedback node
            state = graph.get_state(thread)
            if state.next == ('human_feedback',):
                # Set flag to indicate we are awaiting human feedback
                st.session_state.awaiting_human_feedback = True
                st.write("The assistant is awaiting your feedback.")

            # Increment thread ID for the next conversation
            st.session_state.thread_id = str(int(thread_id) + 1)

    # Ensure the input box is always visible at the bottom

if __name__ == '__main__':
    main()
