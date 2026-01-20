import streamlit as st


def kpi_card(label: str, value: str) -> None:
    html = (
        '<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
