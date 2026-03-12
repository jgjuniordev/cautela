# 🚒 Sistema de Checklist de EPI 

Sistema desenvolvido para **controle operacional de conferência de Equipamentos de Proteção Individual (EPI)** em quartel, com fluxo de verificação entre **Bombeiro → Chefe → Comando**.

O objetivo é garantir **rastreabilidade, segurança operacional e auditoria das inspeções de equipamentos** utilizados nas atividades.

---

# 📋 Funcionalidades

### 👨‍🚒 Bombeiro

* Iniciar checklist de EPI
* Registrar estado dos equipamentos
* Informar irregularidades
* Registrar conferência de saída

### 🧑‍🚒 Chefe de Guarnição

* Conferir checklist de entrada
* Validar ou divergir da avaliação do bombeiro
* Registrar observações adicionais
* Finalizar checklist

### 🎖 Comando

* Visualizar mural de irregularidades
* Registrar **ciente**
* Registrar **resolução de problemas**
* Consultar histórico completo
* Acompanhar checklists em andamento

---

# 🔄 Fluxo do Checklist

O sistema segue **4 etapas operacionais**:

| Etapa | Status no sistema | Responsável              |
| ----- | ----------------- | ------------------------ |
| 25%   | INICIADO          | Bombeiro                 |
| 50%   | AGUARDANDO SAÍDA  | Chefe confere entrada    |
| 75%   | AGUARDANDO FINAL  | Bombeiro confere saída   |
| 100%  | FINALIZADO        | Chefe finaliza checklist |

Fluxo:

```
Bombeiro inicia checklist
        ↓
Chefe confere entrada (50%)
        ↓
Bombeiro confere saída (75%)
        ↓
Chefe finaliza checklist (100%)
```

---

# 🧾 Auditoria Operacional

Quando um item é marcado como **Irregular**, ele aparece automaticamente no **Mural do Comando**.

O comandante pode:

* 👁️ Registrar **Ciente**
* ✅ Registrar **Resolvido**
* Acompanhar divergências entre avaliações

Exemplo de divergência:

```
Bombeiro: Irregular
Chefe: Regular
```

O sistema marca isso como:

```
⚠ Divergência de avaliação
```

---

# 📊 Mural do Comandante

O mural exibe:

* Itens irregulares
* Status do checklist (25%, 50%, 75%, 100%)
* Observações do bombeiro e chefe
* Histórico de auditoria

Funciona como um **painel de acompanhamento operacional**.

---

# 🗂 Estrutura do Banco de Dados

### Tabela `usuarios`

| Campo  | Tipo    |
| ------ | ------- |
| id     | INTEGER |
| nome   | TEXT    |
| login  | TEXT    |
| senha  | TEXT    |
| perfil | TEXT    |

Perfis disponíveis:

* BOMBEIRO
* CHEFE
* COMANDO

---

### Tabela `checklist`

Registro principal da inspeção.

| Campo       | Tipo    |
| ----------- | ------- |
| id          | INTEGER |
| data_hora   | TEXT    |
| bombeiro    | TEXT    |
| bombeiro_id | INTEGER |
| chefe       | TEXT    |
| chefe_id    | INTEGER |
| status      | TEXT    |

Status possíveis:

```
INICIADO (25%)
AGUARDANDO SAÍDA (50%)
AGUARDANDO FINAL (75%)
FINALIZADO (100%)
```

---

### Tabela `itens`

Itens individuais de EPI.

| Campo            | Tipo    |
| ---------------- | ------- |
| id               | INTEGER |
| checklist_id     | INTEGER |
| item_nome        | TEXT    |
| numero           | TEXT    |
| status_bombeiro  | TEXT    |
| obs_bombeiro     | TEXT    |
| status_chefe     | TEXT    |
| observacao_chefe | TEXT    |

---

### Tabela `auditoria_comando`

Registra intervenções do comando.

| Campo          | Tipo    |
| -------------- | ------- |
| id             | INTEGER |
| vistoria_id    | INTEGER |
| equipamento    | TEXT    |
| observacao     | TEXT    |
| bombeiro       | TEXT    |
| data_ciente    | TEXT    |
| comandante     | TEXT    |
| data_resolucao | TEXT    |

---

### Tabela `checklist_checkpoints`

Controle de etapas do checklist.

Permite auditoria detalhada do processo.

---

# ⚙ Tecnologias utilizadas

* **Python**
* **Streamlit**
* **SQLite**
* **Pandas**

Interface web leve para uso interno em rede local do quartel.

---

# 🖥 Instalação

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/seuusuario/checklist-epi-bombeiros.git
cd checklist-epi-bombeiros
```

---

### 2️⃣ Criar ambiente virtual

```bash
python3 -m venv venv
```

Ativar:

Linux / Mac:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

### 3️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Executar o sistema

```bash
streamlit run app.py
```

---

# 🔐 Usuário padrão

Criado automaticamente na inicialização do banco:

```
Login: cmt
Senha: Mh193#
Perfil: COMANDO
```

---

# 📅 Histórico

O sistema permite consultar registros por data:

* Checklists realizados
* Itens avaliados
* Auditorias do comando

---

# 🎯 Objetivo do Projeto

Garantir:

* Segurança operacional
* Controle de equipamentos
* Registro auditável
* Padronização de conferências

Aplicável para **quartéis, brigadas e equipes de resposta a emergências**.

---

# 📜 Licença

Uso autorizado pelo autor estritamente interno e institucional conforme LICENÇA no corpo do projeto.

---

# 👨‍💻 Autor

Projeto desenvolvido para **controle operacional de conferência de EPI em ambiente de bombeiros**.
