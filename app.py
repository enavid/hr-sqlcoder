"""
app.py
------
Entry point.  Run with:  streamlit run app.py

Responsibilities:
- Configure the page layout.
- Register pages via st.navigation.
- Initialise shared session state keys once.
"""

import streamlit as st

st.set_page_config(
    page_title="HR SQLcoder",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared session state defaults ────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []          # list[dict]  {role, content, sql?, result?}

if "server_status" not in st.session_state:
    st.session_state.server_status = None       # None | "online" | "offline"

# ── Navigation ────────────────────────────────────────────────────────────────
chat_page   = st.Page("pages/chat.py",           title="Chat",          icon="💬", default=True)
studio_page = st.Page("pages/prompt_studio.py",  title="Prompt Studio", icon="✏️")

pg = st.navigation([chat_page, studio_page])
pg.run()
