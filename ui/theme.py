import streamlit as st
from backup_data import criar_backup


def aplicar_tema():
    st.markdown(
        """
        <style>
        :root {
            --ink: #e8f0f5;
            --muted: #9aabba;
            --line: #2b3c4c;
            --brand: #2dd4bf;
            --brand-dark: #5eead4;
            --surface: #172635;
            --wash: #0d1722;
        }
        .stApp {
            background: radial-gradient(circle at 15% 0%, #193747 0%, #0d1722 42%, #09111a 100%);
            color: var(--ink);
        }
        [data-testid="stHeader"] {
            background: rgba(9, 17, 26, .82);
        }
        [data-testid="stSidebar"] {
            background: #09111a;
            border-right: 0;
        }
        /* Keep the custom navigation as the single sidebar menu. */
        [data-testid="stSidebarNav"] {
            display: none;
        }
        [data-testid="stSidebar"] * {
            color: #e8f0f5;
        }
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            border-radius: 10px;
        }
        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: -.025em;
        }
        h1 {
            font-size: clamp(2rem, 4vw, 3.25rem) !important;
            font-weight: 800 !important;
        }
        h2 {
            margin-top: 1.5rem !important;
            font-weight: 750 !important;
        }
        .eyebrow {
            color: var(--brand-dark);
            font-size: .75rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin-bottom: .35rem;
        }
        .hero {
            background: linear-gradient(120deg, #102033 0%, #0f766e 100%);
            border-radius: 20px;
            padding: 1.5rem 1.75rem;
            margin: .25rem 0 1.5rem;
            box-shadow: 0 16px 38px rgba(16, 32, 51, .14);
        }
        .hero h1, .hero p, .hero .eyebrow {
            color: white !important;
            margin: 0;
        }
        .hero p {
            opacity: .78;
            margin-top: .5rem;
            font-size: 1rem;
        }
        [data-testid="stMetric"] {
            background: rgba(23, 38, 53, .88);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: .8rem 1rem;
            box-shadow: 0 8px 24px rgba(16, 32, 51, .05);
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 10px;
            border: 1px solid #395063;
            background: #172635;
            color: var(--ink);
            font-weight: 650;
            transition: all .18s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: var(--brand);
            color: var(--brand-dark);
            transform: translateY(-1px);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: .5rem;
            background: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 9px;
            padding: .55rem 1rem;
        }
        div[data-testid="stExpander"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 14px;
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stDateInput"] input {
            background: #101d2a;
            color: var(--ink);
            border-color: var(--line);
        }
        [data-baseweb="select"] > div {
            background: #101d2a;
            border-color: var(--line);
        }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stCaptionContainer"] {
            color: var(--muted);
        }
        [data-testid="stAlert"] {
            background: #172635;
            border-color: var(--line);
        }
        .stPlotlyChart {
            background: transparent;
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecalho(titulo: str, subtitulo: str, eyebrow: str):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{titulo}</h1>
            <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def navegacao():
    st.sidebar.markdown("## 🏃 Atleta AI")
    st.sidebar.caption("Centro de performance · modo local")
    st.sidebar.markdown("---")
    st.sidebar.page_link("app.py", label="Sessões", icon="📊")
    st.sidebar.page_link("pages/perfil_memoria.py", label="Perfil", icon="👤")
    st.sidebar.page_link("pages/memoria.py", label="Memória AI", icon="🧠")
    st.sidebar.page_link("pages/configuracoes.py", label="Configurações", icon="⚙️")
    st.sidebar.markdown("---")
    st.sidebar.caption("Dados locais")
    if st.sidebar.button("💾 Criar backup agora", use_container_width=True):
        try:
            destino = criar_backup()
        except FileNotFoundError as error:
            st.sidebar.error(str(error))
        else:
            st.sidebar.success(f"Backup criado: {destino.name}")
