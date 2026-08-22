"""Unified Statistical Briefs & Tests for ALL EDA Chart Types."""
import numpy as np
import pandas as pd
from scipy import stats


def calculate_hhi(series):
    """Herfindahl-Hirschman Index for categorical concentration (Pie/Bar charts)."""
    if series.empty:
        return 0.0
    counts = series.value_counts(normalize=True)
    return round(float((counts ** 2).sum()), 3)  # 1.0 = monopoly, 0.0 = perfect competition


def calculate_trend_significance(series):
    """Kendall Tau for monotonic trends (Time Series / Line charts)."""
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 5:
        return {"tau": 0, "p_value": 1.0, "trend": "insufficient_data"}
    x = np.arange(len(clean))
    tau, p_value = stats.kendalltau(x, clean.values)
    is_sig = p_value < 0.05
    trend = "upward" if (is_sig and tau > 0.1) else ("downward" if (is_sig and tau < -0.1) else "stable")
    return {"tau": round(float(tau), 3), "p_value": round(float(p_value), 4), "trend": trend}


def calculate_boxplot_stats(groups):
    """Kruskal-Wallis H-test for non-parametric group differences (Box plots)."""
    valid_groups = [pd.to_numeric(pd.Series(g), errors="coerce").dropna().values for g in groups]
    valid_groups = [g for g in valid_groups if len(g) > 1]
    if len(valid_groups) < 2:
        return {"h_stat": 0, "p_value": 1.0, "significant": False}
    try:
        h_stat, p_value = stats.kruskal(*valid_groups)
        return {
            "h_stat": round(float(h_stat), 2),
            "p_value": round(float(p_value), 4),
            "significant": bool(p_value < 0.05)
        }
    except Exception:
        return {"h_stat": 0, "p_value": 1.0, "significant": False}


def generate_executive_brief(chart_type, stats_data, chart_title):
    """
    Translates raw stats into a non-sophisticated, plain-English executive brief.
    Ensures EVERY chart type gets a standardized business summary.
    """
    brief = {"headline": chart_title, "key_insight": "", "statistical_verdict": ""}

    if chart_type in ["histogram", "dist"]:
        skew = stats_data.get("skew", 0)
        if abs(skew) > 1:
            med = stats_data.get("median", "N/A")
            brief["key_insight"] = f"The data is heavily skewed. The median ({med}) is a much safer 'typical' value to use than the average."
        else:
            mean = stats_data.get("mean", "N/A")
            brief["key_insight"] = f"The data is normally distributed. The average ({mean}) accurately represents the typical value."
        brief["statistical_verdict"] = f"Skewness: {round(float(skew), 2) if isinstance(skew, (int, float)) else skew}"

    elif chart_type in ["scatter", "corr"]:
        rho = stats_data.get("rho", 0)
        p = stats_data.get("p_value", 1)
        strength = "strong" if abs(rho) > 0.7 else ("moderate" if abs(rho) > 0.4 else "weak")
        direction = "positive (they move together)" if rho > 0 else "negative (they move oppositely)"
        brief["key_insight"] = f"There is a {strength} {direction} relationship. As one increases, the other tends to {'increase' if rho > 0 else 'decrease'}."
        brief["statistical_verdict"] = f"Spearman rho: {rho} ({'Significant' if p < 0.05 else 'Insignificant'}, p={p})"

    elif chart_type in ["bar", "cat", "pie"]:
        hhi = stats_data.get("hhi", 0)
        if hhi > 0.25:
            brief["key_insight"] = "The distribution is highly concentrated. A few dominant categories hold the vast majority of volume."
        else:
            brief["key_insight"] = "The distribution is well-diversified across multiple categories with healthy competition."
        brief["statistical_verdict"] = f"Concentration Index (HHI): {hhi}"

    elif chart_type in ["box", "numcat"]:
        sig = stats_data.get("significant", False)
        if sig:
            brief["key_insight"] = "There is a statistically significant difference between these groups. The variations you see are real, not random noise."
        else:
            brief["key_insight"] = "Despite visual variations, the groups are statistically similar. Differences are likely due to normal variance."
        brief["statistical_verdict"] = f"Kruskal-Wallis test: {'Statistically Significant (p < 0.05)' if sig else 'Not Significant (p >= 0.05)'}"

    elif chart_type in ["line", "timeseries"]:
        trend = stats_data.get("trend", "stable")
        p = stats_data.get("p_value", 1)
        if trend != "stable" and p < 0.05:
            brief["key_insight"] = f"There is a clear, statistically significant {trend} trend over time. This is a reliable directional movement, not random fluctuation."
        else:
            brief["key_insight"] = "The metrics are relatively stable over time without significant directional drift."
        brief["statistical_verdict"] = f"Kendall Tau: {stats_data.get('tau', 0)} (p={p})"

    else:
        brief["key_insight"] = "Review the visual distribution and summary metrics below for patterns and anomalies."
        brief["statistical_verdict"] = "Verified Standard EDA"

    return brief
