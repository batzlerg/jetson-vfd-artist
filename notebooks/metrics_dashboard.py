import marimo as mo
import pandas as pd
from code_metrics import analyze_code
from analyze import (
    summary,
    pattern_performance,
    recent_failures,
    success_rate_trend,
    bookmarks,
    downvotes,
)

__generated_with = "0.9.0"
app = mo.App()


@app.cell
def __(mo):
    mo.md("# VFD Artist Metrics Dashboard")


@app.cell
def __(mo):
    mo.md("## Generation Summary")


@app.cell
def __(summary):
    summary_df = summary()
    return summary_df,


@app.cell
def __(mo, summary_df):
    mo.ui.dataframe(summary_df)


@app.cell
def __(mo):
    mo.md("## Pattern Performance")


@app.cell
def __(pattern_performance):
    pattern_df = pattern_performance()
    return pattern_df,


@app.cell
def __(mo, pattern_df):
    mo.ui.dataframe(pattern_df)


@app.cell
def __(mo):
    mo.md("## Recent Failures")


@app.cell
def __(recent_failures):
    failures_df = recent_failures()
    return failures_df,


@app.cell
def __(mo, failures_df):
    mo.ui.dataframe(failures_df)


@app.cell
def __(mo):
    mo.md("## Success Rate Trend")


@app.cell
def __(success_rate_trend):
    trend_df = success_rate_trend()
    return trend_df,


@app.cell
def __(mo, trend_df):
    mo.ui.dataframe(trend_df)


@app.cell
def __(mo):
    mo.md("## Bookmarked Animations")


@app.cell
def __(bookmarks):
    bookmarks_df = bookmarks()
    return bookmarks_df,


@app.cell
def __(mo, bookmarks_df):
    mo.ui.dataframe(bookmarks_df)


@app.cell
def __(mo):
    mo.md("## Downvoted Animations")


@app.cell
def __(downvotes):
    downvotes_df = downvotes()
    return downvotes_df,


@app.cell
def __(mo, downvotes_df):
    mo.ui.dataframe(downvotes_df)
