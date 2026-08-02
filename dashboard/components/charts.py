import plotly.express as px
from utils.styles import CHART_COLORS

CHART_TEMPLATE = "plotly_dark"


def line_chart(df, x, y, title, height=450, labels=None, color=None):
    fig = px.line(
        df,
        x=x,
        y=y,
        markers=True,
        title=title,
        labels=labels,
        color=color,
        template=CHART_TEMPLATE,
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin={"t": 40, "b": 40, "l": 40, "r": 40},
    )
    fig.update_xaxes(title_text=x.replace("_", " ").title(), showgrid=False)
    fig.update_yaxes(title_text=(" / ".join(y) if isinstance(y, (list, tuple)) else y).replace("_", " ").title(), showgrid=False)

    return fig


def bar_chart(df, x, y, title, height=450, orientation="v", color=None, text_auto=".2s", labels=None):
    if orientation == "h":
        fig = px.bar(
            df.sort_values(y),
            x=x,
            y=y,
            orientation="h",
            title=title,
            labels=labels,
            color=color,
            text_auto=text_auto,
            template=CHART_TEMPLATE,
            color_discrete_sequence=CHART_COLORS,
        )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            title=title,
            labels=labels,
            color=color,
            text_auto=text_auto,
            template=CHART_TEMPLATE,
            color_discrete_sequence=CHART_COLORS,
        )

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin={"t": 40, "b": 40, "l": 40, "r": 40},
        showlegend=False,
    )
    fig.update_xaxes(title_text=x.replace("_", " ").title(), showgrid=False)
    fig.update_yaxes(title_text=y.replace("_", " ").title(), showgrid=False)

    return fig


def grouped_bar_chart(df, x, y, color, title, height=450, facet_col=None, labels=None):
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        facet_col=facet_col,
        title=title,
        labels=labels,
        template=CHART_TEMPLATE,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        margin={"t": 40, "b": 40, "l": 40, "r": 40},
    )
    fig.update_xaxes(title_text=x.replace("_", " ").title(), showgrid=False)
    fig.update_yaxes(title_text=y.replace("_", " ").title(), showgrid=False)

    return fig
