# components/dialogs.py

import streamlit as st
from tools.data_saver import save_data

@st.dialog("Salvar datos...")
def save_dialog(translations):
    st.markdown(f"#### {translations['want_to_save_data']}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(translations['yes'], key="save_button"):
            with st.spinner(translations['saving_data']):
                save_message = save_data(st.session_state.data_to_save)
                st.session_state.data_to_save = None
                st.session_state.show_save_prompt = False
                if save_message:
                    st.success(f"{translations['data_saved']}, URL: https://docs.google.com/spreadsheets/d/11SchtVPK9FmF9LHnSNLgWCRjczHiofbNH_jvh91uBZo/edit?usp=sharing")
    with col2:
        if st.button(translations['no'], key="no_save_button"):
            st.session_state.data_to_save = None
            st.session_state.show_save_prompt = False
            st.rerun()
