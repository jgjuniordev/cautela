import streamlit as st
from database import conectar


def tela():

    # 🔐 Somente COMANDO pode acessar
    if "usuario" not in st.session_state:
        st.error("Faça login primeiro.")
        return

    if st.session_state.get("perfil") != "COMANDO":
        st.error("Apenas COMANDO pode cadastrar usuários.")
        return

    st.title("👥 Cadastro de Usuários")

    st.write(f"Comando logado: **{st.session_state['usuario']}**")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    nome = st.text_input("Nome completo")
    novo_usuario = st.text_input("Login")
    nova_senha = st.text_input("Senha", type="password")

    # 🔥 AGORA INCLUINDO BOMBEIRO
    perfil = st.selectbox("Perfil", ["BOMBEIRO", "CHEFE", "COMANDO"])

    if st.button("Cadastrar"):

        if not nome or not novo_usuario or not nova_senha:
            st.error("Preencha todos os campos.")
            return

        conn = conectar()
        cursor = conn.cursor()

        # Verifica duplicado
        cursor.execute("SELECT id FROM usuarios WHERE login = ?", (novo_usuario,))
        if cursor.fetchone():
            st.error("Usuário já existe.")
            conn.close()
            return

        cursor.execute("""
            INSERT INTO usuarios (nome, login, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, (nome, novo_usuario, nova_senha, perfil))

        conn.commit()
        conn.close()

        st.success(f"Usuário {novo_usuario} cadastrado como {perfil} com sucesso!")
        st.rerun()