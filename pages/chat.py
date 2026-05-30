"""
pages/chat.py
-------------
Chat page. Renders the conversation, handles SQL generation
and optional query execution against PostgreSQL.
"""

from __future__ import annotations

import streamlit as st

from core.llm import GenerationResult, generate_sql, health_check
from core.prompt import build_prompt
from core.storage import get_active_template
from core.database import run_query, QueryResult


# ── CSS ───────────────────────────────────────────────────────────────────────

SIDEBAR_CSS = """
<style>
/* ── sidebar shell ── */
[data-testid="stSidebar"] {
    background: #0f1119 !important;
    border-right: 1px solid #272a38 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem 1rem;
}

/* ── logo ── */
.sidebar-logo {
    font-size: 17px;
    font-weight: 600;
    color: #d0d4f0;
    letter-spacing: .3px;
    margin-bottom: 1.2rem;
}
.sidebar-logo span { color: #3b6ef5; }

/* ── section label ── */
.sidebar-label {
    font-size: 10px;
    font-weight: 600;
    color: #4a5070;
    text-transform: uppercase;
    letter-spacing: .8px;
    margin-bottom: .4rem;
}

/* ── status pill ── */
.status-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #272a38;
    background: #161825;
    margin-bottom: 1rem;
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.status-dot.online  { background: #34d399; box-shadow: 0 0 6px #34d39966; }
.status-dot.offline { background: #f87171; }
.status-dot.unknown { background: #6b7280; }
.status-text {
    font-size: 12px;
    color: #8090b8;
}

/* ── active prompt pill ── */
.prompt-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #253060;
    background: #192040;
    margin-bottom: 1rem;
}
.prompt-pill-icon { font-size: 14px; }
.prompt-pill-name { font-size: 13px; color: #82aaff; font-weight: 500; }

/* ── sidebar divider ── */
[data-testid="stSidebar"] hr {
    border-color: #272a38 !important;
    margin: .75rem 0 !important;
}

/* ── clear button ── */
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid #272a38 !important;
    color: #6070a0 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: #3b6ef5 !important;
    color: #82aaff !important;
}
</style>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _check_server() -> None:
    result = health_check()
    st.session_state.server_status = "online" if result.online else "offline"


def _render_result(result: QueryResult) -> None:
    if not result.success:
        st.error(f"Query error: {result.error}")
        return
    st.caption(f"  {result.row_count} row{'s' if result.row_count != 1 else ''}  ·  {result.elapsed_ms} ms")
    st.dataframe(result.data, use_container_width=True)


def _render_message(entry: dict) -> None:
    role = entry["role"]
    with st.chat_message(role):
        if role == "user":
            st.write(entry["content"])
            return

        sql: str = entry.get("sql", "")
        gen_error: str | None = entry.get("error")

        if gen_error:
            st.error(gen_error)
            return

        st.code(sql, language="sql")

        exec_result: QueryResult | None = entry.get("result")
        exec_dismissed: bool = entry.get("dismissed", False)

        if exec_result is not None:
            _render_result(exec_result)
        elif not exec_dismissed:
            col_run, col_skip, _ = st.columns([1, 1, 6])
            if col_run.button("Run on DB", key=f"run_{entry['id']}"):
                with st.spinner("Executing query…"):
                    entry["result"] = run_query(sql)
                st.rerun()
            if col_skip.button("Dismiss", key=f"skip_{entry['id']}"):
                entry["dismissed"] = True
                st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar() -> None:
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-logo">HR <span>SQL</span>coder</div>', unsafe_allow_html=True)
        st.divider()

        # Server status
        _check_server()
        status = st.session_state.get("server_status", "unknown")
        dot_class = status if status in ("online", "offline") else "unknown"
        label = "llama3-sqlcoder · online" if status == "online" else f"Ollama · {status}"
        st.markdown(
            f'<div class="status-pill">'
            f'<div class="status-dot {dot_class}"></div>'
            f'<span class="status-text">{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # Active prompt
        active = get_active_template()
        st.markdown('<div class="sidebar-label">Active prompt</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="prompt-pill">'
            f'<span class="prompt-pill-icon">✏️</span>'
            f'<span class="prompt-pill-name">{active.name}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _sidebar()

    st.title("HR SQL Assistant")

    history: list[dict] = st.session_state.chat_history

    for entry in history:
        _render_message(entry)

    question = st.chat_input("Ask a question about HR data…")
    if not question:
        return

    user_entry = {"id": len(history), "role": "user", "content": question}
    history.append(user_entry)

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL…"):
            active = get_active_template()
            prompt = build_prompt(question, active.template)
            result: GenerationResult = generate_sql(prompt)

        assistant_entry: dict = {"id": len(history), "role": "assistant"}

        if not result.success:
            assistant_entry["sql"] = ""
            assistant_entry["error"] = result.error
            st.error(result.error)
        else:
            assistant_entry["sql"] = result.sql
            st.code(result.sql, language="sql")

            col_run, col_skip, _ = st.columns([1, 1, 6])
            if col_run.button("Run on DB", key=f"run_{assistant_entry['id']}"):
                with st.spinner("Executing query…"):
                    assistant_entry["result"] = run_query(result.sql)
            if col_skip.button("Dismiss", key=f"skip_{assistant_entry['id']}"):
                assistant_entry["dismissed"] = True

        history.append(assistant_entry)

        if assistant_entry.get("result"):
            _render_result(assistant_entry["result"])

    st.rerun()


main()
