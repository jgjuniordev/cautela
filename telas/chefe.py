import streamlit as st
from database import conectar
from datetime import datetime, timedelta, time, date
from typing import cast


# =====================================
# LOGIN GENÉRICO
# =====================================
def tela_login(perfis_permitidos):
    st.title("Login")

    login = st.text_input("Login")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not login or not senha:
            st.error("Preencha login e senha")
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, senha, perfil
            FROM usuarios
            WHERE login = ?
        """, (login,))

        resultado = cursor.fetchone()
        conn.close()

        if resultado is None:
            st.error("Usuário não encontrado.")
            return

        usuario_id, senha_bd, perfil = resultado

        if senha == senha_bd and perfil.upper() in perfis_permitidos:
            st.session_state["usuario"] = login
            st.session_state["usuario_id"] = usuario_id
            st.session_state["perfil"] = perfil.upper()
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Senha incorreta ou perfil sem permissão.")





# =====================================
# STATUS AUTOMÁTICO
# =====================================
def calcular_status_checklist(checklist_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT etapa FROM checklist_checkpoints
        WHERE checklist_id = ?
    """, (checklist_id,))

    etapas = [row[0] for row in cursor.fetchall()]
    conn.close()

    if "validacao_final_chefe" in etapas:
        return "FINALIZADO (100%)", 100

    if "saida_bombeiro" in etapas:
        return "AGUARDANDO FINAL (75%)", 75

    if "validacao_inicial_chefe" in etapas:
        return "AGUARDANDO SAÍDA (50%)", 50

    if "entrada_bombeiro" in etapas:
        return "INICIADO (25%)", 25

    return "NÃO INICIADO (0%)", 0


def atualizar_status_checklist(checklist_id):
    status, _ = calcular_status_checklist(checklist_id)
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE checklist SET status=? WHERE id=?", (status, checklist_id))
    conn.commit()
    conn.close()


# =====================================
# BADGE STATUS
# =====================================
def badge_status(status: str):
    if status.upper() == "IRREGULAR":
        return '<span style="background-color:#ff4d4d;color:white;padding:4px 10px;border-radius:8px;font-weight:bold;">IRREGULAR</span>'
    elif status.upper() == "NAO_CAUTELADO":
        return '<span style="background-color:#e9ecef;color:#495057;padding:4px 10px;border-radius:8px;font-weight:bold;">NÃO CAUTELADO</span>'
    elif status.upper() == "CONFORME":
        return '<span style="background-color:#28a745;color:white;padding:4px 10px;border-radius:8px;font-weight:bold;">CONFORME</span>'
    else:
        return status


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
        ("entrada_bombeiro", "Bombeiro Entrada"),
        ("validacao_inicial_chefe", "Chefe de Socorro - Conferência Inicial"),
        ("saida_bombeiro", "Bombeiro Saída"),
        ("validacao_final_chefe", "Chefe de Socorro - Conferência Final"),
    ]

    st.markdown("### 📊 Progresso do Checklist")
    for codigo, nome in fases:
        if codigo in etapas:
            st.markdown(f"✅ **{nome}**")
        else:
            st.markdown(f"⬜ {nome}")


# =====================================
# TELA PRINCIPAL CHEFE
# =====================================
def tela():
    if "usuario" not in st.session_state:
        tela_login(["CHEFE"])
        return

    if st.session_state.get("perfil") != "CHEFE":
        st.warning("Sessão encerrada.")
        st.session_state.clear()
        tela_login(["CHEFE"])
        return

    st.title("👨‍🚒 Tela do Chefe de Socorro")
    st.write(f"Chefe de Socorro logado: **{st.session_state['usuario']}**")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    # =====================================
    # 🔔 REGRA AUTOMÁTICA 15 DIAS
    # =====================================

    DATA_BASE = datetime(2025, 1, 15)  # marco oficial
    hoje = datetime.now()

    dias_passados = (hoje.date() - DATA_BASE.date()).days

    if dias_passados >= 0 and dias_passados % 15 == 0:

        st.error("""
    ⚠️ CONFERÊNCIA GERAL OBRIGATÓRIA

    Conforme escala automática de 15 dias,
    o Chefe de Socorro logado deve realizar:

    • Conferência visual completa de todos os materiais
    • Verificação de integridade
    • Comunicação de irregularidades
    • Registro formal após conferência
    """)
    else:
        st.info("✅ Não há alerta para conferência completa dos EPI's hoje.")

    # =====================================
    # DATA PLANTÃO
    # =====================================
    raw_data = st.date_input(
        "Selecione a data de início do plantão (08h)",
        value=datetime.today().date()
    )
    data_inicio = cast(date, raw_data[0]) if isinstance(raw_data, tuple) else cast(date, raw_data)
    inicio_plantao = datetime.combine(data_inicio, time(8, 0))
    fim_plantao = inicio_plantao + timedelta(hours=24)
    inicio_str = inicio_plantao.strftime("%Y-%m-%d %H:%M:%S")
    fim_str = fim_plantao.strftime("%Y-%m-%d %H:%M:%S")

    st.info(f"Plantão selecionado: {inicio_str} até {fim_str}")

    # =====================================
    # BUSCAR CHECKLISTS PENDENTES
    # =====================================
    conn = conectar()
    cursor = conn.cursor()
    st.header("Checklists do Plantão")

    cursor.execute("""
        SELECT * FROM checklist
        WHERE data_hora BETWEEN ? AND ?
        ORDER BY data_hora ASC
    """, (inicio_str, fim_str))
    checklists = cursor.fetchall()
    conn.close()

    if not checklists:
        st.info("Não há checklists.")
        return

    for chk in checklists:
        checklist_id = chk[0]
        status_atual, percentual = calcular_status_checklist(checklist_id)

        # MOSTRAR APENAS CHECKLISTS NÃO FINALIZADOS
        if status_atual == "FINALIZADO":
            continue

        with st.expander(f"Checklist ID: {checklist_id} | Bombeiro: {chk[2]} | Status: {status_atual}"):
            
        
            # Registrar chefe responsável pelo checklist
            conn_reg = conectar()
            cursor_reg = conn_reg.cursor()

            cursor_reg.execute("""
            UPDATE checklist
            SET chefe = ?
            WHERE id = ? AND (chefe IS NULL OR chefe = '')
            """, (st.session_state["usuario"], checklist_id))

            conn_reg.commit()
            conn_reg.close()

            mostrar_fases_checklist(checklist_id)

            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM itens WHERE checklist_id=?", (checklist_id,))
            itens = cursor.fetchall()
            conn.close()

            dados_obs = []
            for it in itens:
                st.write(f"**{it[2]}**")
                st.text(f"Número: {it[3]}")
                st.markdown(f"Status Bombeiro: {badge_status(it[4])}", unsafe_allow_html=True)
                st.text(f"Observação Bombeiro: {it[5]}")

                status_radio = st.radio(
                    f"Status Chefe de Socorro - {it[2]}",
                    ["Conforme", "Irregular", "Não cautelado"],
                    key=f"{it[0]}_chefe"
                )

                obs_c = ""
                if status_radio == "Não cautelado":
                    status_c = "nao_cautelado"
                else:
                    status_c = status_radio
                    if status_c == "Irregular":
                        obs_c = st.text_input(f"Observação Chefe de Socorro- {it[2]}", key=f"{it[0]}_obs")

                dados_obs.append((it[0], status_c, obs_c))

            # =====================================================
            # CONFERÊNCIA INICIAL
            # =====================================================
            if status_atual == "INICIADO (25%)":
                if st.button(f"Confirmar Conferência Inicial (50%) - {checklist_id}", key=f"inicial_{checklist_id}"):
                    conn_local = conectar()
                    cursor_local = conn_local.cursor()
                    cursor_local.execute("""
                        INSERT OR IGNORE INTO checklist_checkpoints
                        (checklist_id, usuario_id, perfil, etapa, ordem, data_hora)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        checklist_id,
                        st.session_state["usuario_id"],
                        "CHEFE",
                        "validacao_inicial_chefe",
                        2,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    conn_local.commit()
                    conn_local.close()
                    atualizar_status_checklist(checklist_id)
                    st.success("Conferência inicial registrada.")
                    st.rerun()

            # =====================================================
            # CONFERÊNCIA FINAL
            # =====================================================
            elif status_atual == "AGUARDANDO FINAL (75%)":
                if st.button(f"Finalizar Conferência Final (100%) - {checklist_id}", key=f"final_{checklist_id}"):
                    conn_local = conectar()
                    cursor_local = conn_local.cursor()

                    # Atualizar status de cada item
                    for item_id, status_c, obs_c in dados_obs:
                        cursor_local.execute("""
                            UPDATE itens
                            SET status_chefe=?, observacao_chefe=?
                            WHERE id=?
                        """, (status_c, obs_c, item_id))

                    # Inserir checkpoint final
                    cursor_local.execute("""
                        INSERT OR IGNORE INTO checklist_checkpoints
                        (checklist_id, usuario_id, perfil, etapa, ordem, data_hora)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        checklist_id,
                        st.session_state["usuario_id"],
                        "CHEFE",
                        "validacao_final_chefe",
                        4,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))

                    conn_local.commit()
                    conn_local.close()
                    atualizar_status_checklist(checklist_id)
                    st.success("Checklist FINALIZADO (100%)")
                    st.rerun() # garante atualização imediata