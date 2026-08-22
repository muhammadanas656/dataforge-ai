import os
import json
from html import escape
from src.eda_engine import run_full_eda


def render_eda_html(dataset_id: str):
    eda = run_full_eda(dataset_id)
    results = eda.get("results", [])

    os.makedirs(f"exports/{dataset_id}", exist_ok=True)
    path = f"exports/{dataset_id}/eda_report.html"

    cards = []

    for r in results:
        explanation = r.get("chart_explanation", {})
        stats = json.dumps(r.get("stats", {}), indent=2)

        rows = ""
        data = r.get("data", [])
        if data:
            cols = list(data[0].keys())
            header = "".join(f"<th>{escape(str(c))}</th>" for c in cols)
            body = ""
            for row in data[:50]:
                body += "<tr>" + "".join(f"<td>{escape(str(row.get(c, '')))}</td>" for c in cols) + "</tr>"
            rows = f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"

        helps = "".join(f"<li>{escape(x)}</li>" for x in explanation.get("helps_with", []))

        cards.append(f"""
        <section class="card">
          <h2>{escape(r.get("title", "Analysis"))}</h2>
          <p class="insight">💡 {escape(r.get("insight", ""))}</p>

          <div class="explain">
            <p><b>Chart Type:</b> {escape(explanation.get("plain_name", r.get("chart_type", "table")))}</p>
            <p><b>What is this?</b> {escape(explanation.get("simple_definition", ""))}</p>
            <p><b>Why was it used?</b> {escape(r.get("why_selected", explanation.get("why_used", "")))}</p>
            <p><b>How to read it:</b> {escape(explanation.get("how_to_read", ""))}</p>
            <p><b>What does it help with:</b></p>
            <ul>{helps}</ul>
          </div>

          <h3>Data Representation Preview</h3>
          {rows}

          <h3>Statistical Companions & Proofs</h3>
          <pre>{escape(stats)}</pre>
        </section>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>DataForge EDA Report - {dataset_id}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      margin: 0;
      padding: 32px;
      line-height: 1.5;
    }}
    .wrap {{
      max-width: 960px;
      margin: auto;
    }}
    .card {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(15,23,42,.06);
    }}
    h1 {{ margin-bottom: 4px; color: #1e1b4b; font-size: 26px; }}
    h2 {{ margin-top: 0; color: #0f172a; font-size: 18px; }}
    h3 {{ font-size: 14px; margin-top: 20px; color: #334155; }}
    .muted {{ color: #64748b; font-size: 14px; margin-top: 2px; }}
    .insight {{
      background: #eef2ff;
      border-left: 4px solid #6366f1;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 13px;
      color: #312e81;
      font-weight: 500;
    }}
    .explain {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px;
      margin-top: 16px;
      font-size: 13px;
    }}
    .explain p {{ margin: 6px 0; }}
    .explain ul {{ margin: 6px 0; padding-left: 20px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 12px;
      font-family: monospace;
    }}
    th, td {{
      border-bottom: 1px solid #e2e8f0;
      padding: 8px 10px;
      text-align: left;
    }}
    th {{
      background: #f1f5f9;
      font-family: sans-serif;
      font-weight: 600;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.05em;
    }}
    pre {{
      background: #0f172a;
      color: #34d399;
      padding: 14px;
      border-radius: 10px;
      overflow-x: auto;
      font-size: 12px;
    }}
    @media print {{
      body {{ background: white; padding: 0; }}
      .card {{ break-inside: avoid; box-shadow: none; border: 1px solid #cbd5e1; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>DataForge AI — Explainable EDA Report</h1>
    <p class="muted"><b>Dataset ID:</b> {dataset_id}</p>
    <p class="muted">This standalone report provides both statistical findings and plain-English educational context explaining why each chart representation was chosen and how to read it.</p>
    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;"/>
    {''.join(cards)}
  </div>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "path": path,
        "message": "EDA HTML report generated",
        "tip": "Open this file in a browser and use Print > Save as PDF to export as PDF."
    }
