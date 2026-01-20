from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
for path in (ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from src.memos import build_club_memo
from src.utils import MEMOS_DIR, PROCESSED_DIR

st.set_page_config(page_title="Club Strategy Memos", layout="wide")

@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "club_metrics.csv")


def main() -> None:
    st.title("Club Strategy Memos")
    df = load_data()
    latest = df[df["season"] == df["season"].max()]

    club = st.selectbox("Select club", latest["team_name"].sort_values())
    row = latest[latest["team_name"] == club].iloc[0]

    memo_text = build_club_memo(row)
    st.markdown(memo_text)

    file_name = f"{row['team_id']}_memo.md"
    st.download_button(
        label="Download memo",
        data=memo_text,
        file_name=file_name,
        mime="text/markdown",
    )

    st.subheader("League Memo")
    league_memo_path = Path(MEMOS_DIR) / "league_memo.md"
    if league_memo_path.exists():
        st.markdown(league_memo_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
