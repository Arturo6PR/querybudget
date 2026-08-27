from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def write_report(analysis: dict[str, Any], destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    budget_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['team'])}</td><td>${row['actual_usd']:.2f}</td>"
        f"<td>${row['budget_usd']:.2f}</td><td>{row['utilization_pct']}%</td>"
        f"<td class='{row['status'].lower()}'>{row['status']}</td></tr>"
        for row in analysis["budgets"]
    )
    finding_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['query_id'])}</td><td>{html.escape(row['team'])}</td>"
        f"<td>{html.escape(' / '.join(row['rules']))}</td><td>${row['cost_usd']:.2f}</td>"
        f"<td>${row['estimated_savings_usd']:.2f}</td></tr>"
        for row in analysis["findings"]
    ) or "<tr><td colspan='5'>no findings</td></tr>"
    summary = analysis["summary"]
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>QueryBudget / warehouse spend review</title><style>
:root{{--bg:#0e1012;--panel:#17191c;--line:#35393e;--ink:#e1e3e5;--muted:#92979d;--ok:#8eb69a;--warn:#d2a85f;--over:#d2766e}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px ui-monospace,SFMono-Regular,Consolas,monospace}}main{{max-width:1120px;margin:auto;padding:42px 24px}}
header{{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:24px}}h1{{font-size:25px;margin:0 0 8px}}h2{{font-size:13px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin:30px 0 10px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line)}}.metric{{padding:17px;border-right:1px solid var(--line);background:var(--panel)}}.metric:last-child{{border:0}}.metric b{{display:block;font-size:24px;margin-top:8px}}
table{{width:100%;table-layout:fixed;border-collapse:collapse;background:var(--panel)}}th,td{{padding:12px;text-align:left;border:1px solid var(--line);overflow-wrap:anywhere}}th{{color:var(--muted);font-weight:500}}.pass{{color:var(--ok)}}.warn{{color:var(--warn)}}.over{{color:var(--over)}}
pre{{white-space:pre-wrap;border:1px solid var(--line);background:var(--panel);padding:16px;color:var(--muted)}}details{{margin-top:30px}}summary{{cursor:pointer;color:var(--muted);letter-spacing:.12em;font-size:13px}}@media(max-width:720px){{.grid{{grid-template-columns:1fr 1fr}}}}
</style></head><body><main><header><div>WAREHOUSE FINOPS / EXPLAINABLE POLICY</div><h1>QUERYBUDGET / SPEND REVIEW</h1><div>deterministic fingerprints · budget ownership · no automated query rewrites</div></header>
<section class="grid"><div class="metric">OBSERVED COST<b>${summary['total_cost_usd']:.2f}</b></div><div class="metric">POTENTIAL SAVINGS<b>${summary['potential_savings_usd']:.2f}</b></div><div class="metric">FLAGGED QUERIES<b>{summary['flagged_queries']}</b></div><div class="metric">TEAMS OVER<b>{summary['teams_over_budget']}</b></div></section>
<h2>Budget control</h2><table><thead><tr><th>OWNER</th><th>ACTUAL</th><th>BUDGET</th><th>UTILIZATION</th><th>STATUS</th></tr></thead><tbody>{budget_rows}</tbody></table>
<h2>Prioritized evidence</h2><table><thead><tr><th>QUERY</th><th>OWNER</th><th>RULES</th><th>COST</th><th>EST. SAVINGS</th></tr></thead><tbody>{finding_rows}</tbody></table>
<details><summary>MACHINE-READABLE ANALYSIS</summary><pre>{html.escape(json.dumps(analysis, indent=2))}</pre></details></main></body></html>"""
    path.write_text(document, encoding="utf-8")
    return path
