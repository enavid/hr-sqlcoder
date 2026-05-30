"""
pages/prompt_studio.py
-----------------------
Prompt Studio page. Create, edit, activate and delete named prompt templates.
Templates are persisted to prompts.json via core.storage.
"""

from __future__ import annotations

import streamlit as st

from core.prompt import DEFAULT_TEMPLATE, build_prompt
from core.storage import (
    PromptTemplate,
    delete_template,
    get_active_template,
    list_templates,
    save_template,
    set_active_template,
)


# ── CSS ───────────────────────────────────────────────────────────────────────

STUDIO_CSS = """
<style>
[data-testid="stSidebar"] {
    background: #0f1119 !important;
    border-right: 1px solid #272a38 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1rem 1rem; }

.sidebar-logo { font-size: 17px; font-weight: 600; color: #d0d4f0; margin-bottom: 1.2rem; }
.sidebar-logo span { color: #3b6ef5; }

.sidebar-label {
    font-size: 10px; font-weight: 600; color: #4a5070;
    text-transform: uppercase; letter-spacing: .8px; margin-bottom: .5rem;
}

.active-badge {
    display: inline-block;
    font-size: 11px; padding: 2px 10px; border-radius: 20px;
    background: #192040; color: #82aaff;
    border: 1px solid #253060; margin-bottom: 1rem;
}

/* template buttons in sidebar */
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid #272a38 !important;
    color: #8090b8 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: #3b6ef5 !important;
    color: #82aaff !important;
    background: #192040 !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    border-color: #3b6ef5 !important;
    background: #192040 !important;
    color: #82aaff !important;
}

[data-testid="stSidebar"] hr { border-color: #272a38 !important; margin: .75rem 0 !important; }
</style>
"""


# ── Constants ─────────────────────────────────────────────────────────────────

_UNSAVED_MARKER = " *"


# ── Session state helpers ─────────────────────────────────────────────────────

def _init_state() -> None:
    if "studio_selected" not in st.session_state:
        st.session_state.studio_selected = None
    if "studio_draft" not in st.session_state:
        st.session_state.studio_draft = {}


def _get_draft(name: str, original: str) -> str:
    return st.session_state.studio_draft.get(name, original)


def _set_draft(name: str, value: str) -> None:
    st.session_state.studio_draft[name] = value


def _clear_draft(name: str) -> None:
    st.session_state.studio_draft.pop(name, None)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar(templates: list[PromptTemplate], active_name: str) -> None:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">HR <span>SQL</span>coder</div>', unsafe_allow_html=True)
        st.divider()

        st.markdown('<div class="sidebar-label">Prompt Studio</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="active-badge">Active: {active_name}</div>', unsafe_allow_html=True)

        selected = st.session_state.studio_selected

        for t in templates:
            label = t.name + (_UNSAVED_MARKER if t.name in st.session_state.studio_draft else "")
            is_current = t.name == selected
            if st.button(label, key=f"sel_{t.name}", use_container_width=True,
                         type="primary" if is_current else "secondary"):
                st.session_state.studio_selected = t.name
                st.rerun()

        st.divider()
        if st.button("+ New prompt", use_container_width=True):
            st.session_state.studio_selected = None
            st.rerun()


# ── New template panel ────────────────────────────────────────────────────────

def _new_template_panel() -> None:
    st.subheader("New prompt template")

    name = st.text_input("Name", placeholder="e.g. Education Focus")
    template_text = st.text_area(
        "Template",
        value=DEFAULT_TEMPLATE,
        height=420,
        help="Use {schema_context} and {question} as placeholders.",
    )

    col_save, _ = st.columns([2, 8])
    if col_save.button("Save", type="primary", use_container_width=True):
        if not name.strip():
            st.warning("Please enter a name for the template.")
            return
        save_template(name.strip(), template_text)
        st.session_state.studio_selected = name.strip()
        st.success(f'Template "{name}" saved.')
        st.rerun()


# ── Edit panel ────────────────────────────────────────────────────────────────

def _edit_template_panel(template: PromptTemplate, active_name: str) -> None:
    is_active = template.name == active_name

    col_title, col_badge = st.columns([6, 2])
    col_title.subheader(template.name)
    if is_active:
        col_badge.markdown(
            '<span style="display:inline-block;margin-top:8px;padding:3px 12px;'
            'border-radius:20px;background:#192040;color:#34d399;'
            'border:1px solid #1a4030;font-size:12px;">Active</span>',
            unsafe_allow_html=True,
        )

    current_text = _get_draft(template.name, template.template)
    edited = st.text_area(
        "Template",
        value=current_text,
        height=360,
        key=f"editor_{template.name}",
        help="Use {schema_context} and {question} as placeholders.",
    )

    if edited != current_text:
        _set_draft(template.name, edited)

    has_unsaved = template.name in st.session_state.studio_draft

    col_save, col_activate, col_discard, col_delete, _ = st.columns([1.5, 1.5, 1.5, 1.5, 4])

    if col_save.button("Save", type="primary", disabled=not has_unsaved, use_container_width=True):
        save_template(template.name, edited)
        _clear_draft(template.name)
        st.success("Saved.")
        st.rerun()

    if not is_active:
        if col_activate.button("Set active", use_container_width=True):
            set_active_template(template.name)
            st.success(f'"{template.name}" is now active.')
            st.rerun()

    if has_unsaved:
        if col_discard.button("Discard", use_container_width=True):
            _clear_draft(template.name)
            st.rerun()

    if not is_active:
        if col_delete.button("Delete", use_container_width=True):
            delete_template(template.name)
            st.session_state.studio_selected = None
            _clear_draft(template.name)
            st.rerun()

    st.divider()
    with st.expander("Preview rendered prompt", expanded=False):
        sample_q = st.text_input(
            "Sample question",
            value="How many active employees are there?",
            key=f"preview_q_{template.name}",
        )
        try:
            st.code(build_prompt(sample_q, edited), language="text")
        except FileNotFoundError as exc:
            st.warning(str(exc))


# ── Parsed rules panel ────────────────────────────────────────────────────────

def _parsed_rules_panel(template_text: str) -> None:
    st.caption("Detected rules")
    lines = template_text.splitlines()
    rules = [ln.strip() for ln in lines if ln.strip().startswith("-")]

    if not rules:
        st.info("No bullet rules detected.")
        return

    for rule in rules:
        cleaned = rule.lstrip("- ").strip()
        if any(k in cleaned for k in ("is_active", "is_current", "is_latest")):
            st.markdown(f"🔵 `{cleaned}`")
        elif "GROUP BY" in cleaned.upper():
            st.markdown(f"🟢 `{cleaned}`")
        elif any(k in cleaned.upper() for k in ("ORDER BY", "LIMIT")):
            st.markdown(f"🟠 `{cleaned}`")
        else:
            st.markdown(f"⚪ `{cleaned}`")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _init_state()
    st.markdown(STUDIO_CSS, unsafe_allow_html=True)

    templates = list_templates()
    active = get_active_template()

    _sidebar(templates, active.name)

    selected_name = st.session_state.studio_selected

    if selected_name is None:
        _new_template_panel()
        return

    match = next((t for t in templates if t.name == selected_name), None)
    if match is None:
        st.warning("Template not found.")
        st.session_state.studio_selected = None
        st.rerun()
        return

    col_editor, col_rules = st.columns([3, 1])
    with col_editor:
        _edit_template_panel(match, active.name)
    with col_rules:
        _parsed_rules_panel(_get_draft(match.name, match.template))


main()
