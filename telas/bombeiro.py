import streamlit as st
from datetime import datetime, timedelta
from database import conectar

ITENS_EPI = [
    "Jaqueta de Incêndio - CIE",
    "Calça de Incêndio - CIE",
    "Capacete de Incêndio - CIE",
    "Luva de Incêndio - CIE",
    "Botas de Incêndio - CIE",
    "Balaclava de Incêndio - CIE",
    "Colete de APH",
    "Óculos de Proteção",
    "Capacete de Resgate - RVE",
    "Calça - Multimissão",
    "Jaqueta - Multimissão",
    "Luva de Resgate - RVE",
    "Luva de Raspa",
    "Botas Pampena",
    "Calça - Incêndio Florestal",
    "Jaqueta - Incêndio Florestal",
]

NUMEROS_EQUIPAMENTO = [str(i) for i in range(1, 15)]

# =====================================
# LOGIN BOMBEIRO
# =====================================
def tela_login():
    st.title("Login Bombeiro Comunitário")
    login = st.text_input("Login")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, senha, perfil FROM usuarios WHERE login=?", (login,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            usuario_id, senha_bd, perfil = resultado
            if senha == senha_bd and perfil.upper() == "BOMBEIRO":
                st.session_state["usuario"] = login
                st.session_state["usuario_id"] = usuario_id
                st.session_state["perfil"] = "BOMBEIRO"
                st.rerun()
        st.error("Login inválido.")

# =====================================
# STATUS CHECKLIST
# =====================================
def calcular_status_checklist(checklist_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT etapa FROM checklist_checkpoints WHERE checklist_id=?", (checklist_id,))
    etapas = [row[0] for row in cursor.fetchall()]
    conn.close()

    if "validacao_final_chefe" in etapas:
        return "FINALIZADO", 100
    if "saida_bombeiro" in etapas:
        return "AGUARDANDO FINAL (75%)", 75
    if "validacao_inicial_chefe" in etapas:
        return "AGUARDANDO SAÍDA", 50
    if "entrada_bombeiro" in etapas:
        return "INICIADO (25%)", 25
    return "NÃO INICIADO", 0

def atualizar_status_checklist(checklist_id):
    status, _ = calcular_status_checklist(checklist_id)
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE checklist SET status=? WHERE id=?", (status, checklist_id))
    conn.commit()
    conn.close()

# =====================================
# CHECKPOINT VISUAL
# =====================================
def mostrar_fases_checklist(checklist_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT etapa FROM checklist_checkpoints WHERE checklist_id=?", (checklist_id,))
    etapas = [row[0] for row in cursor.fetchall()]
    conn.close()

    fases = [
        ("entrada_bombeiro", "BC - Início de Plantão"),
        ("validacao_inicial_chefe", "Chefe Conferência Inicial"),
        ("saida_bombeiro", "BC - Saída de Plantão"),
        ("validacao_final_chefe", "Chefe de Soc. - Conferência Final"),
    ]

    for codigo, nome in fases:
        if codigo in etapas:
            st.markdown(f"✅ **{nome}**")
        else:
            st.markdown(f"⬜ {nome}")

# =====================================
# BUSCAR CHECKLIST PENDENTE AJUSTADO
# =====================================
def buscar_checklist_pendente():
    if "usuario" not in st.session_state:
        return None

    conn = conectar()
    cursor = conn.cursor()
    hoje = datetime.now()
    inicio = hoje.replace(hour=8, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(hours=24)

    cursor.execute("""
        SELECT id, status FROM checklist
        WHERE bombeiro=? AND data_hora BETWEEN ? AND ?
        ORDER BY id DESC LIMIT 1
    """, (st.session_state["usuario"], inicio, fim))
    res = cursor.fetchone()
    conn.close()

    if res is None:
        return None

    checklist_id, status = res
    if status.upper() == "FINALIZADO":
        return None
    return checklist_id

# =====================================
# TELA PRINCIPAL BOMBEIRO AJUSTADA
# =====================================
def tela():
    if "usuario" not in st.session_state:
        tela_login()
        return

    st.title("👨‍🚒 Tela do Bombeiro Comunitário")
    st.write(f"Bombeiro Comunitário logado: **{st.session_state['usuario']}**")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # ===========================
    # Buscar checklist pendente
    # ===========================
    checklist_id = buscar_checklist_pendente()
    st.session_state["checklist_id"] = checklist_id

    # ===========================
    # BOTÃO INICIAR CHECKLIST
    # ===========================
    if checklist_id is None:
        if st.button("Iniciar Checklist"):
            # Criar novo checklist
            conn = conectar()
            cursor = conn.cursor()
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO checklist (data_hora, bombeiro) VALUES (?, ?)",
                           (data_hora, st.session_state["usuario"]))
            checklist_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO checklist_checkpoints
                (checklist_id, usuario_id, perfil, etapa, ordem, data_hora)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (checklist_id, st.session_state["usuario_id"], "BOMBEIRO", "entrada_bombeiro", 1, data_hora))

            conn.commit()
            conn.close()
            st.session_state["checklist_id"] = checklist_id
            atualizar_status_checklist(checklist_id)
            st.rerun()
        else:
            st.info("Nenhum checklist ativo. Clique em 'Iniciar Checklist' para criar um novo.")
        return

    # ===========================
    # EXPANDER COM CHECKLIST E ITENS
    # ===========================
    status_atual, percentual = calcular_status_checklist(checklist_id)

    # Botão para iniciar novo checklist quando o anterior estiver finalizado
    if status_atual.upper() == "FINALIZADO":
        st.success("Checklist finalizado pelo Chefe. Você pode iniciar um novo checklist.")
        
        if st.button("Iniciar Novo Checklist"):
            # Criar novo checklist
            conn = conectar()
            cursor = conn.cursor()
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO checklist (data_hora, bombeiro) VALUES (?, ?)",
                        (data_hora, st.session_state["usuario"]))
            novo_checklist_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO checklist_checkpoints
                (checklist_id, usuario_id, perfil, etapa, ordem, data_hora)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (novo_checklist_id, st.session_state["usuario_id"], "BOMBEIRO", "entrada_bombeiro", 1, data_hora))

            conn.commit()
            conn.close()

            st.session_state["checklist_id"] = novo_checklist_id
            atualizar_status_checklist(novo_checklist_id)
            st.rerun()  # recarrega a tela com o novo checklist
        return  # não mostrar o checklist antigo
    # ===========================
    # Mostrar checklist atual
    # ===========================
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checklist WHERE id=?", (checklist_id,))
    chk = cursor.fetchone()
    conn.close()

    with st.expander(f"Checklist ID: {checklist_id} | Bombeiro: {chk[2]} | Status: {status_atual}"):
        mostrar_fases_checklist(checklist_id)

        # --- Itens de EPI ---
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itens WHERE checklist_id=?", (checklist_id,))
        itens = cursor.fetchall()
        conn.close()

        dados_itens = []

        for item_nome in ITENS_EPI:
            st.subheader(item_nome)
            item_db = next((i for i in itens if i[2] == item_nome), None)
            numero_val = item_db[3] if item_db else ""
            status_val = item_db[4] if item_db else ""
            obs_val = item_db[5] if item_db else ""

            # Número ou tamanho
            if item_nome in ["Calça - Multimissão", "Jaqueta - Multimissão"]:
                numero = st.selectbox(
                    f"Tamanho - {item_nome}", ["", "P", "M", "G", "GG", "EG"],
                    index=["", "P", "M", "G", "GG", "EG"].index(numero_val) if numero_val in ["P","M","G","GG","EG"] else 0,
                    key=f"{item_nome}_num"
                )
            else:
                numero = st.selectbox(
                    f"Número - {item_nome}", [""] + NUMEROS_EQUIPAMENTO,
                    index=([""] + NUMEROS_EQUIPAMENTO).index(numero_val) if numero_val in NUMEROS_EQUIPAMENTO else 0,
                    key=f"{item_nome}_num"
                )

            # Status
            status_radio = st.radio(
                f"Status - {item_nome}",
                ["Conforme", "Irregular", "Não cautelado"],
                index=["Conforme","Irregular","Não cautelado"].index(status_val) if status_val in ["Conforme","Irregular","Não cautelado"] else 0,
                key=f"{item_nome}_status"
            )

            obs = ""
            if status_radio == "Irregular":
                obs = st.text_input(f"Observação - {item_nome}", value=obs_val, key=f"{item_nome}_obs")

            dados_itens.append((item_nome, numero, status_radio, obs))

        # --- Botão Salvar Itens ---
        if st.button("Salvar Itens do Checklist"):
            conn = conectar()
            cursor = conn.cursor()
            for item_nome, numero, status_radio, obs in dados_itens:
                if next((i for i in itens if i[2] == item_nome), None):
                    cursor.execute("""
                        UPDATE itens
                        SET numero=?, status_bombeiro=?, obs_bombeiro=?
                        WHERE checklist_id=? AND item_nome=?
                    """, (numero, status_radio, obs, checklist_id, item_nome))
                else:
                    cursor.execute("""
                        INSERT INTO itens (checklist_id, item_nome, numero, status_bombeiro, obs_bombeiro)
                        VALUES (?, ?, ?, ?, ?)
                    """, (checklist_id, item_nome, numero, status_radio, obs))
            conn.commit()
            conn.close()
            st.success("Itens salvos com sucesso!")

        # --- Botão registrar saída ---
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT etapa FROM checklist_checkpoints WHERE checklist_id=?", (checklist_id,))
        etapas = [row[0] for row in cursor.fetchall()]
        conn.close()

        if "validacao_inicial_chefe" in etapas and "saida_bombeiro" not in etapas:
            if st.button("Registrar Saída do Plantão"):
                conn = conectar()
                cursor = conn.cursor()
                for item_nome, numero, status_radio, obs in dados_itens:
                    cursor.execute("""
                        UPDATE itens
                        SET numero=?, status_bombeiro=?, obs_bombeiro=?
                        WHERE checklist_id=? AND item_nome=?
                    """, (numero, status_radio, obs, checklist_id, item_nome))

                cursor.execute("""
                    INSERT INTO checklist_checkpoints
                    (checklist_id, usuario_id, perfil, etapa, ordem, data_hora)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    checklist_id,
                    st.session_state["usuario_id"],
                    "BOMBEIRO",
                    "saida_bombeiro",
                    3,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

                conn.commit()
                conn.close()
                atualizar_status_checklist(checklist_id)
                st.success("Saída registrada com sucesso!")
                st.rerun()
        elif "saida_bombeiro" in etapas:
            st.info("Saída já registrada.")
        else:
            st.info("Aguardando conferência inicial do Chefe.")