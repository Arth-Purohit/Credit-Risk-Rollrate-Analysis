"""
visualize.py
------------
Shared plotting helpers (seaborn/matplotlib + plotly) used by the
vintage, roll-rate, and segment analysis scripts.
"""

import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

sns.set_theme(style="whitegrid", palette="viridis")
CHART_DIR = "outputs/charts"
os.makedirs(CHART_DIR, exist_ok=True)


def save_heatmap(pivot_df, title, filename, fmt=".1f", cmap="Reds", figsize=(12, 6)):
    plt.figure(figsize=figsize)
    sns.heatmap(pivot_df, annot=True, fmt=fmt, cmap=cmap, cbar_kws={"label": "%"})
    plt.title(title, fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(CHART_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  chart saved: {path}")
    return path


def save_lineplot(df, x, y, hue, title, filename, ylabel=None, figsize=(11, 6)):
    plt.figure(figsize=figsize)
    sns.lineplot(data=df, x=x, y=y, hue=hue, marker="o")
    plt.title(title, fontsize=13, fontweight="bold")
    plt.ylabel(ylabel or y)
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.join(CHART_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  chart saved: {path}")
    return path


def save_plotly_line(df, x, y, color, title, filename):
    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title)
    fig.update_layout(template="plotly_white", hovermode="x unified")
    path = os.path.join(CHART_DIR, filename)
    fig.write_html(path)
    print(f"  interactive chart saved: {path}")
    return path
