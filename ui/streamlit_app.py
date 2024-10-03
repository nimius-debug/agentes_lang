# main.py

import streamlit as st
import asyncio
from langchain_core.messages import AIMessage, HumanMessage

# Importar componentes personalizados
from ui.components.ui_components import render_header, render_features
from ui.components.user_input import handle_user_input
from ui.components.dialogs import save_dialog

def run_app():
    st.set_page_config(page_title="Asistente con Integración de Herramientas", page_icon="✨", layout="wide")

    # Renderizar encabezado y características
    render_header()
    render_features()
    st.write(" ")
    st.divider()
    # Inicializar variables de estado de sesión
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'thread' not in st.session_state:
        st.session_state.thread = {"configurable": {"thread_id": "1"}}
    if 'data_to_save' not in st.session_state:
        st.session_state.data_to_save = None

    # Layout principal
    body_col1, body_col2 = st.columns([1, 1])
    with body_col1:
        # Mostrar historial de conversación
        st.header("Historial de conversación", divider="blue")
        container = st.container(height=400)
        with container:
            for message in st.session_state.conversation_history:
                if isinstance(message, HumanMessage):
                    with st.chat_message("user", avatar="🧑‍💻"):
                        st.write(message.content)
                elif isinstance(message, AIMessage):
                    with st.chat_message("assistant", avatar="✨"):
                        st.write(message.content)

        # Manejo de entrada del usuario
        st.header("Conversación actual", divider="blue")
        user_input = st.chat_input("Escribe tu mensaje")
        if user_input:
            asyncio.run(handle_user_input(user_input))

        # Diálogo para guardar datos
        if st.session_state.get('show_save_prompt', False) and st.session_state.data_to_save:
            save_dialog()

    # Información de depuración
    with body_col2:
        if st.toggle("Mostrar agentes' 🧠"):
            st.write("Información de depuración:")
            st.write(f"data_to_save: {st.session_state.data_to_save}")
            st.write(f"conversation_history: {st.session_state.conversation_history}")


