import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime, date
from typing import Union
import urllib.parse


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
            SELECT senha, perfil
            FROM usuarios
            WHERE login = ?
        """, (login,))

        resultado = cursor.fetchone()
        conn.close()

        if resultado is None:
            st.error("Usuário não encontrado.")
            return

        senha_bd, perfil = resultado

        if senha == senha_bd and perfil.upper() in perfis_permitidos:
            st.session_state["usuario"] = login
            st.session_state["perfil"] = perfil.upper()
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Senha incorreta ou perfil sem permissão.")


# =====================================
# TELA PRINCIPAL DO COMANDO
# =====================================

def tela():

    if "usuario" not in st.session_state:
        tela_login(["COMANDO"])
        return

    if st.session_state.get("perfil") != "COMANDO":
        st.error("Acesso permitido apenas para perfil COMANDO.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
        return

    # CONTROLE DE TELA
    if "tela_comando" not in st.session_state:
        st.session_state["tela_comando"] = "mural"

    st.title("📊 Mural do Comandante")
    st.write(f"Comandante logado: **{st.session_state['usuario']}**")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # ESTILO VISUAL RESTAURADO
    st.markdown("""
        <style>
        .postit {
            background-color: #f1f5f9;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 3px 3px 12px rgba(0,0,0,0.15);
            margin-bottom: 25px;
        }
        .postit-critico {
            background-color: #fee2e2;
        }
        .badge {
            background-color: #facc15;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            color: #78350f;
        }
        .obs-bombeiro {
            font-size: 13px;
            color: #1d4ed8;
        }
        .obs-chefe {
            font-size: 13px;
            color: #b91c1c;
        }
        </style>
    """, unsafe_allow_html=True)

    conn = conectar()
    cursor = conn.cursor()

    # BUSCAR CHECKLISTS IRREGULARES + STATUS
    cursor.execute("""
        SELECT DISTINCT c.id, c.bombeiro, c.chefe, c.data_hora, c.status
        FROM checklist c
        JOIN itens i ON c.id = i.checklist_id
        WHERE i.status_chefe = 'Irregular'
        OR i.status_bombeiro = 'Irregular'
    """)

    checklists_irregulares = cursor.fetchall()

    # CONTAR PENDENTES
    cursor.execute("""
        SELECT COUNT(*)
        FROM checklist
        WHERE status IN ('INICIADO (25%)', 'AGUARDANDO SAÍDA (50%)', 'AGUARDANDO FINAL (75%)')
    """)
    total_pendentes = cursor.fetchone()[0]

    # MÉTRICAS
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Checklists com Irregularidades", len(checklists_irregulares))

    with col2:
        if st.button(
            f"📌 {total_pendentes} - Checklist em andamento/pendentes",
            use_container_width=True
        ):
            st.session_state["tela_comando"] = "pendentes"
            st.rerun()

    st.divider()

    # ==============================
    # TELA PENDENTES
    # ==============================

    if st.session_state["tela_comando"] == "pendentes":

        col_voltar, col_titulo = st.columns([1, 4])

        with col_voltar:
            if st.button("⬅ Voltar"):
                st.session_state["tela_comando"] = "mural"
                st.rerun()

        with col_titulo:
            st.subheader("📌 Checklists em andamento/pendentes")

        df_pendentes = pd.read_sql_query("""
            SELECT *
            FROM checklist
            WHERE status IN ('INICIADO (25%)', 'AGUARDANDO SAÍDA (50%)', 'AGUARDANDO FINAL (75%)')
            ORDER BY data_hora DESC
        """, conn)

        if not df_pendentes.empty:
            st.dataframe(df_pendentes, use_container_width=True)
        else:
            st.info("Nenhum checklist aguardando avaliação.")

        conn.close()
        return

    # ==============================
    # MURAL
    # ==============================

    if checklists_irregulares:

        cols = st.columns(3)

        for idx, checklist in enumerate(checklists_irregulares):
            checklist_id, bombeiro, chefe, data_hora, status = checklist

            cursor.execute("""
                SELECT id, item_nome,
                       status_bombeiro,
                       obs_bombeiro,
                       status_chefe,
                       observacao_chefe
                FROM itens
                WHERE checklist_id = ?
                AND (
                    status_chefe = 'Irregular'
                    OR status_bombeiro = 'Irregular'
                )
            """, (checklist_id,))

            itens_irregulares = cursor.fetchall()

            with cols[idx % 3]:

                conteudo = ""
                card_class = "postit"
                badge_html = ""

                for item in itens_irregulares:
                    (
                        item_id,
                        nome_item,
                        status_bombeiro,
                        obs_bombeiro,
                        status_chefe,
                        obs_chefe
                    ) = item

                    if status_bombeiro == "Irregular" and status_chefe == "Irregular":
                        card_class = "postit postit-critico"

                    if (status_bombeiro == "Irregular" and status_chefe != "Irregular") or \
                       (status_chefe == "Irregular" and status_bombeiro != "Irregular"):
                        badge_html = "<div class='badge'>⚠ Divergência de avaliação</div><br>"

                    obs_b = obs_bombeiro if status_bombeiro == "Irregular" else "Sem irregularidade"
                    obs_c = obs_chefe if status_chefe == "Irregular" else "Sem irregularidade"

                    conteudo += (
                        "<div style='margin-bottom:10px;'>"
                        f"<b>🧥 {nome_item}</b><br>"
                        f"<span class='obs-bombeiro'>👨‍🚒 <b>Bombeiro:</b> {obs_b}</span><br>"
                        f"<span class='obs-chefe'>🧑‍🚒 <b>Chefe:</b> {obs_c}</span>"
                        "</div>"
                    )
                # DEFINIR ÍCONE DO STATUS
                if status == "INICIADO (25%)":
                    icone_status = "🟡 25%"

                elif status == "AGUARDANDO SAÍDA (50%)":
                    icone_status = "🟠 50%"

                elif status == "AGUARDANDO FINAL (75%)":
                    icone_status = "🔵 75%"

                elif status == "FINALIZADO (100%)":
                    icone_status = "🟢 100%"

                else:
                    icone_status = "⚪"

                card = (
                    f"<div class='{card_class}'>"
                    f"<h4>🚨 Conferência em: - {icone_status}</h4>"
                    f"{badge_html}"
                    f"<b>👨‍🚒 Bombeiro:</b> {bombeiro}<br>"
                    f"<b>🧑‍🚒 Chefe:</b> {chefe if chefe else 'Não informado'}<br>"
                    f"<b>📅 Data/Hora:</b> {data_hora}"
                    "<hr>"
                    f"{conteudo}"
                    "</div>"
                )

                st.markdown(card, unsafe_allow_html=True)

                # ==============================
                # BOTÕES CIENTE / RESOLVIDO
                # ==============================

                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM auditoria_comando
                    WHERE vistoria_id IN (
                        SELECT id FROM itens WHERE checklist_id = ?
                    )
                    AND data_ciente IS NOT NULL
                """, (checklist_id,))

                ja_deu_ciente = cursor.fetchone()[0] > 0

                col_ciente, col_resolvido = st.columns(2)

                # BOTÃO CIENTE (ESQUERDA)
                with col_ciente:
                    if st.button(
                        "👁️ Ciente",
                        key=f"ciente_{checklist_id}",
                        disabled=ja_deu_ciente
                    ):
                        comandante = st.session_state["usuario"]

                        for item in itens_irregulares:
                            item_id = item[0]
                            cursor.execute("""
                                INSERT INTO auditoria_comando
                                (vistoria_id, data_ciente, comandante)
                                VALUES (?, ?, ?)
                            """, (
                                item_id,
                                datetime.now().strftime("%d/%m/%Y %H:%M"),
                                comandante
                            ))

                        conn.commit()
                        st.success("Ciente registrado com sucesso.")
                        st.rerun()

                # BOTÃO RESOLVIDO (DIREITA)
                with col_resolvido:
                    if st.button(
                        "✅ Resolvido",
                        key=f"resolver_{checklist_id}"
                    ):
                        comandante = st.session_state["usuario"]

                        for item in itens_irregulares:
                            item_id = item[0]
                            nome_item = item[1]
                            obs_bombeiro = item[3]
                            obs_chefe = item[5]

                            observacao_final = (
                                f"Bombeiro: {obs_bombeiro or 'Sem obs'} | "
                                f"Chefe: {obs_chefe or 'Sem obs'}"
                            )

                            cursor.execute("""
                                INSERT INTO auditoria_comando 
                                (vistoria_id, equipamento, observacao, bombeiro, data_ciente, comandante, data_resolucao)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                item_id,
                                nome_item,
                                observacao_final,
                                bombeiro,
                                data_hora,
                                comandante,
                                datetime.now().strftime("%d/%m/%Y %H:%M")
                            ))

                            cursor.execute("""
                                UPDATE itens
                                SET status_chefe = 'RESOLVIDO',
                                    status_bombeiro = 'RESOLVIDO'
                                WHERE id = ?
                            """, (item_id,))

                        cursor.execute("""
                            UPDATE checklist
                            SET status = 'RESOLVIDO'
                            WHERE id = ?
                        """, (checklist_id,))

                        conn.commit()
                        st.success("Pendências resolvidas com sucesso.")
                        st.rerun()
                    else:
                        st.success("Aguardando resolução")

    # ==============================
    # HISTÓRICO
    # ==============================

    st.divider()
    st.subheader("📜 Histórico por Data")

    data_busca: Union[date, tuple[date, date], None] = st.date_input(
        "Selecione a data:",
        value=None
    )

    if st.button("🔎 Buscar Histórico"):

        if isinstance(data_busca, tuple):
            data_busca = data_busca[0]

        if not data_busca:
            st.warning("Selecione uma data.")
            conn.close()
            return

        data_formatada = data_busca.strftime("%Y-%m-%d")

        df_checklist = pd.read_sql_query(
            "SELECT * FROM checklist WHERE data_hora LIKE ?",
            conn,
            params=(f"{data_formatada}%",)
        )

        df_itens = pd.read_sql_query("""
            SELECT * FROM itens
            WHERE checklist_id IN (
                SELECT id FROM checklist
                WHERE data_hora LIKE ?
            )
        """, conn, params=(f"{data_formatada}%",))

        df_auditoria = pd.read_sql_query(
            "SELECT * FROM auditoria_comando WHERE data_ciente LIKE ?",
            conn,
            params=(f"{data_formatada}%",)
        )

        aba1, aba2, aba3 = st.tabs(["📋 Checklist", "🧥 Itens", "🗂 Auditoria"])

        with aba1:
            st.dataframe(df_checklist, use_container_width=True) if not df_checklist.empty else st.info("Nenhum checklist encontrado.")

        with aba2:
            st.dataframe(df_itens, use_container_width=True) if not df_itens.empty else st.info("Nenhum item encontrado.")

        with aba3:
            st.dataframe(df_auditoria, use_container_width=True) if not df_auditoria.empty else st.info("Nenhum registro encontrado.")

    conn.close()