import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import asyncio
from app.graph import graph
from app.utils import convert_history_to_messages

st.set_page_config(page_title="Nexia - Assistente de Agendamentos", page_icon="🤖")
st.title("🤖 Nexia - Assistente de Agendamentos")

if "history" not in st.session_state:
    st.session_state.history = []

if "state" not in st.session_state:
    st.session_state.state = {"messages": []}

user_input = st.chat_input("Digite sua mensagem:")

if user_input:
    st.session_state.history.append(("Usuário", user_input))
    st.session_state.state["messages"] = convert_history_to_messages(st.session_state.history)

    with st.spinner("Nexia está pensando..."):
        result = asyncio.run(graph.ainvoke(st.session_state.state))
        messages = result.pop("messages", [])
        response = messages[-1].content if messages else "Desculpe, não entendi sua solicitação."

    st.session_state.history.append(("Nexia", response))
    st.session_state.state.update(result)
    st.session_state.state["messages"] = convert_history_to_messages(st.session_state.history)

st.markdown("---")
for speaker, text in st.session_state.history:
    with st.chat_message("user" if speaker == "Usuário" else "assistant", avatar="👤" if speaker == "Usuário" else "🤖"):
        st.markdown(text)
