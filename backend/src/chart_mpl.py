import base64
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # server-safe headless backend
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import seaborn as sns
from src.utils import logger

# Styling parameters
PRIMARY = "#6366f1"
CAT = ["#6366f1", "#8b5cf6", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#14b8a6", "#84cc16", "#f97316"]

def _create_fig(figsize=(8, 4.5)):
    """Create a completely isolated, thread-safe Matplotlib Figure without touching pyplot global state."""
    fig = Figure(figsize=figsize, dpi=160, facecolor="white")
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.grid(True, linestyle="--", alpha=0.5, color="#e2e8f0")
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#cbd5e1")
    ax.tick_params(colors="#475569", labelsize=9)
    return fig, ax

def _b64(fig):
    """Serialize figure to Base64 PNG and release memory cleanly."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white", dpi=160)
    fig.clf()
    val = base64.b64encode(buf.getvalue()).decode()
    buf.close()
    return val

def render_dist(df, col, title, chart_type="histogram"):
    fig, ax = _create_fig(figsize=(8, 4.5))
    s = df[col].dropna()
    if len(s) == 0:
        ax.text(0.5, 0.5, "No valid numeric data", ha="center", va="center", color="#64748b")
        return _b64(fig)

    if chart_type == "box":
        sns.boxplot(y=s, color=PRIMARY, ax=ax)
        ax.set_ylabel(col, fontsize=10, color="#334155")
    else:
        sns.histplot(s, bins=min(30, max(5, int(np.sqrt(len(s))))), kde=True, color=PRIMARY, edgecolor=".15", alpha=0.85, ax=ax)
        ax.set_xlabel(col, fontsize=10, color="#334155")
        ax.set_ylabel("Count", fontsize=10, color="#334155")

    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    return _b64(fig)

def render_bar(df, col, title, chart_type="bar"):
    vc = df[col].fillna("MISSING").astype(str).value_counts().head(10)
    fig, ax = _create_fig(figsize=(8, 4.5))
    if len(vc) == 0:
        ax.text(0.5, 0.5, "No categorical data", ha="center", va="center", color="#64748b")
        return _b64(fig)

    if chart_type == "pie":
        ax.pie(vc.values, labels=vc.index, autopct="%1.1f%%", colors=CAT, textprops={"fontsize": 9, "color": "#1e293b"})
    else:
        sns.barplot(x=vc.values, y=vc.index, hue=vc.index, palette=CAT[:len(vc)], legend=False, ax=ax, orient="h")
        ax.set_xlabel("Count", fontsize=10, color="#334155")
        ax.set_ylabel("", fontsize=10)

    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    return _b64(fig)

def render_scatter(df, x, y, title):
    sub = df[[x, y]].dropna()
    if len(sub) > 2000:
        sub = sub.sample(2000, random_state=42)
    fig, ax = _create_fig(figsize=(8, 4.8))
    if len(sub) == 0:
        ax.text(0.5, 0.5, "No valid data pairs", ha="center", va="center", color="#64748b")
        return _b64(fig)

    sns.scatterplot(data=sub, x=x, y=y, alpha=0.5, s=24, color=PRIMARY, ax=ax)
    if len(sub) >= 3 and sub[x].nunique() > 1:
        try:
            z = np.polyfit(sub[x], sub[y], 1)
            p = np.poly1d(z)
            xs = np.linspace(sub[x].min(), sub[x].max(), 50)
            ax.plot(xs, p(xs), "--", color="#ef4444", lw=1.5, label="Trendline")
            ax.legend(frameon=True, facecolor="white", edgecolor="#e2e8f0")
        except Exception:
            pass

    ax.set_xlabel(x, fontsize=10, color="#334155")
    ax.set_ylabel(y, fontsize=10, color="#334155")
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    return _b64(fig)

def render_box(df, cat, num, title):
    order = df.groupby(cat)[num].median().sort_values(ascending=False).index[:10]
    fig, ax = _create_fig(figsize=(8, 4.8))
    sns.boxplot(data=df, x=cat, y=num, order=order, palette=CAT[:len(order)], ax=ax)
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
    ax.set_xlabel(cat, fontsize=10, color="#334155")
    ax.set_ylabel(num, fontsize=10, color="#334155")
    return _b64(fig)

def render_heatmap(df, title):
    num_df = df.select_dtypes(include="number")
    # Drop zero-variance columns to prevent NaN matrices
    valid_cols = [c for c in num_df.columns if num_df[c].nunique(dropna=True) > 1]
    fig, ax = _create_fig(figsize=(7, 6))
    if len(valid_cols) < 2:
        ax.text(0.5, 0.5, "Requires >= 2 numeric columns with non-zero variance", ha="center", va="center", color="#64748b")
        return _b64(fig)

    corr = num_df[valid_cols].corr(method="spearman").fillna(0)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, annot=len(corr) <= 10, fmt=".2f", cmap="vlag", center=0, mask=mask,
                vmin=-1, vmax=1, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    return _b64(fig)

def render_topn(df, cat, num, title):
    g = df.groupby(cat)[num].sum().sort_values(ascending=False).head(12)
    fig, ax = _create_fig(figsize=(8, 4.5))
    if len(g) == 0:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", color="#64748b")
        return _b64(fig)

    sns.barplot(x=g.values, y=g.index, palette="viridis", ax=ax, orient="h")
    ax.set_xlabel(f"Sum of {num}", fontsize=10, color="#334155")
    ax.set_ylabel("", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    return _b64(fig)

def render_analysis(df, kind, parts, chart_type, title):
    try:
        if kind == "dist":
            return render_dist(df, parts[1], title, chart_type or "histogram")
        if kind == "cat":
            return render_bar(df, parts[1], title, chart_type or "bar")
        if kind == "corr":
            return render_heatmap(df, title)
        if kind == "scatter":
            return render_scatter(df, parts[1], parts[2], title)
        if kind == "numcat":
            return render_box(df, parts[1], parts[2], title)
        if kind == "topn":
            return render_topn(df, parts[1], parts[2], title)
        if kind == "ai":
            sub_type = parts[1]
            cols = parts[2].split(",")
            if sub_type == "numeric_distribution":
                return render_dist(df, cols[0], title, chart_type or "histogram")
            if sub_type == "category_breakdown":
                return render_bar(df, cols[0], title, chart_type or "bar")
            if sub_type == "numeric_relationship":
                return render_scatter(df, cols[0], cols[1], title)
            if sub_type == "numeric_by_category":
                return render_box(df, cols[0], cols[1], title)
            if sub_type == "correlation":
                return render_heatmap(df, title)
            if sub_type == "top_n":
                return render_topn(df, cols[0], cols[1], title)
        return None
    except Exception as e:
        logger.error(f"chart render failed: {e}")
        return None
