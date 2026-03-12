import streamlit as st
from telas import bombeiro, chefe, comandante, cadastro
from database import criar_tabelas

st.set_page_config(page_title="Sistema Operacional", layout="wide")

criar_tabelas()

st.sidebar.title("👨‍🚒 Sistema Operacional")

# 🔐 Se não estiver logado, mostra login do perfil escolhido
menu = st.sidebar.radio(
    "Selecione o Perfil:",
    ["Bombeiro Comunitário", "Chefe de Socorro", "Comandante"]
)

# ===============================
# CONTROLE DE NAVEGAÇÃO
# ===============================

if menu == "Bombeiro Comunitário":
    bombeiro.tela()

elif menu == "Chefe de Socorro":
    chefe.tela()

elif menu == "Comandante":

    # Submenu interno do Comandante
    submenu = st.sidebar.selectbox(
        "Área do Comando:",
        ["Painel", "Cadastro de Usuários"]
    )

    if submenu == "Painel":
        comandante.tela()

    elif submenu == "Cadastro de Usuários":
        cadastro.tela()


# Para rodar:
# streamlit run app.py --server.address=0.0.0.0 --server.port=8501
