from src.plugins import BaseAnalysis

class DiscountDepthAnalysis(BaseAnalysis):
    name = "discount_depth"

    def applicable(self, profile):
        return any("discount" in c["name"].lower() for c in profile.get("columns", []))

    def run(self, df):
        disc_cols = [c for c in df.columns if "discount" in c.lower()]
        if not disc_cols:
            return None
        col = disc_cols[0]
        s = df[col].dropna()
        deep = int((s > 40).sum())
        total = len(df) if len(df) > 0 else 1
        pct = round(deep / total * 100, 2)

        return {
            "title": "Discount Depth (plugin)",
            "chart_type": "table",
            "x_column": "metric",
            "y_column": "value",
            "data": [
                {"metric": "rows_over_40pct", "value": deep},
                {"metric": "share_pct", "value": pct}
            ],
            "stats": {"deep_count": deep, "total_rows": total, "share_pct": pct},
            "insight": f"{deep} rows ({pct}%) have discount >40%.",
            "representations": ["table", "narrative"]
        }
