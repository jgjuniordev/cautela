import sqlite3

def conectar():
    conn = sqlite3.connect("banco.db", check_same_thread=False)
    return conn


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # ==============================
    # TABELA DE USUÁRIOS
    # ==============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        login TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL
    )
    """)

    # ==============================
    # TABELA DE CHECKLIST
    # ==============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora TEXT,
        bombeiro TEXT,
        bombeiro_id INTEGER,
        chefe TEXT,
        chefe_id INTEGER,
        status TEXT,
        FOREIGN KEY (bombeiro_id) REFERENCES usuarios(id),
        FOREIGN KEY (chefe_id) REFERENCES usuarios(id)
    )
    """)

    # ==============================
    # TABELA DE ITENS
    # ==============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_id INTEGER,
        item_nome TEXT,
        numero TEXT,
        status_bombeiro TEXT,
        obs_bombeiro TEXT,
        status_chefe TEXT,
        observacao_chefe TEXT
    )
    """)

    # ==============================
    # TABELA DO COMANDO
    # ==============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditoria_comando (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vistoria_id INTEGER,
        equipamento TEXT,
        observacao TEXT,
        bombeiro TEXT,
        data_ciente TEXT,
        comandante TEXT,
        data_resolucao TEXT
    )
    """)

    # ==============================
    # TABELA DO CHECKPOINTS
    # ==============================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklist_checkpoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        perfil TEXT NOT NULL,
        etapa TEXT NOT NULL,
        ordem INTEGER NOT NULL,
        data_hora TEXT NOT NULL,
        observacao TEXT,
        FOREIGN KEY (checklist_id) REFERENCES checklist(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        UNIQUE(checklist_id, etapa)
    )
    """)

    # ==============================
    # INSERIR USUÁRIO PADRÃO COMANDO
    # ==============================
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (nome, login, senha, perfil)
        VALUES (?, ?, ?, ?)
    """, ("COMANDO", "cmt", "Mh193#", "COMANDO"))

    conn.commit()
    conn.close()