# main.py

import streamlit as st
import asyncio
import json
from langchain_core.messages import AIMessage, HumanMessage

# Import custom components
from ui.components.ui_components import render_header, render_features
from ui.components.user_input import handle_user_input
from ui.components.dialogs import save_dialog

st.set_page_config(page_title="OptiSales", page_icon="✨", layout="wide")

def load_translations(language):
    with open("translations.json", 'r', encoding='utf-8') as f:
        translations = json.load(f)
    return translations[language]

def run_app():
    # Initialize session state for language
    if 'language' not in st.session_state:
        st.session_state.language = 'en'

    # Language selector
    language = st.sidebar.selectbox('Language / Idioma', options=['Español', 'English'])

    if language == 'English':
        st.session_state.language = 'en'
    else:
        st.session_state.language = 'es'

    # Load translations
    translations = load_translations(st.session_state.language)
    
    render_header(translations)
    render_features(translations)
    st.write(" ")
    st.divider()

    # Initialize session state variables
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'thread' not in st.session_state:
        st.session_state.thread = {"configurable": {"thread_id": "1"}}
    if 'data_to_save' not in st.session_state:
        st.session_state.data_to_save = None

    # Main layout
    body_col1, body_col2 = st.columns([1, 1])
    with body_col1:
        # Display conversation history
        st.header(translations['header'], divider="blue")
        container = st.container(height=500)
        with container:
            for message in st.session_state.conversation_history:
                if isinstance(message, HumanMessage):
                    with st.chat_message("user", avatar="🧑‍💻"):
                        st.write(message.content)
                elif isinstance(message, AIMessage):
                    with st.chat_message("assistant", avatar="✨"):
                        st.write(message.content)

        # Handle user input
        st.header(translations['conversation_current'], divider="blue")
        user_input = st.chat_input(translations['write_message'])
        if user_input:
            asyncio.run(handle_user_input(user_input))

        # Save data dialog
        if st.session_state.get('show_save_prompt', False) and st.session_state.data_to_save:
            save_dialog(translations)

    # Debug information
    with body_col2:
        if st.checkbox(translations['show_agents']):
            st.write(translations['debug_info'])
            st.write(f"{translations['data_to_save']}: {st.session_state.data_to_save}")
            st.write(f"{translations['conversation_history']}: {st.session_state.conversation_history}")

if __name__ == "__main__":
    run_app()
