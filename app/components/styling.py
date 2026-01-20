import streamlit as st


def apply_base_styles() -> None:
    styles = (
        "<style>\n"
        ".kpi-card {background: #111827; color: #f9fafb; padding: 16px; border-radius: 10px; text-align: center;}\n"
        ".kpi-label {font-size: 0.85rem; opacity: 0.8;}\n"
        ".kpi-value {font-size: 1.4rem; font-weight: 600;}\n"
        "</style>"
    )
    st.markdown(styles, unsafe_allow_html=True)
