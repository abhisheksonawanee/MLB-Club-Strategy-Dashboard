import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = ""):
    fig = px.line(df, x=x, y=y, color=color, title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str, hover: str, title: str = ""):
    fig = px.scatter(df, x=x, y=y, color=color, hover_name=hover, title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = ""):
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def waterfall_chart(base: float, change: float, title: str = ""):
    fig = go.Figure(go.Waterfall(
        name="Revenue",
        orientation="v",
        measure=["absolute", "relative"],
        x=["Base", "Scenario"],
        y=[base, change],
        connector={"line": {"color": "#9ca3af"}},
    ))
    fig.update_layout(title=title, margin=dict(l=10, r=10, t=40, b=10))
    return fig
