"""Render a QualityReport as a self-contained, offline HTML document.

Zinc & Sky palette, theme-aware (light/dark via prefers-color-scheme), no CDN,
no external assets, so the whole report is one portable file you can email to a
client as the sign-off artifact.
"""

from __future__ import annotations

from html import escape

from spreadsheet_cleaner.core.models import (
    DIMENSION_ORDER,
    QualityReport,
    Severity,
)

_CSS = """
:root{
  --bg:#F5F7F8; --surface:#fff; --raised:#fff; --line:#E4E7EA;
  --ink:#09090B; --muted:#52525B; --faint:#71717A;
  --accent:#0E7490; --accent-2:#155E6E; --accent-soft:#E0F5F9; --accent-soft-bd:#A5E1ED;
  --good:#047857; --good-bg:#ECFDF5; --warn:#B45309; --warn-bg:#FFFBEB; --bad:#DC2626; --bad-bg:#FEF2F2;
  --shadow:0 1px 2px rgba(20,30,50,.06),0 8px 24px rgba(20,30,50,.06);
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#09090B; --surface:#18181B; --raised:#27272A; --line:#27272A;
    --ink:#F5F7F8; --muted:#C3C7CE; --faint:#8A8F98;
    --accent:#38BDF8; --accent-2:#7DD3FC; --accent-soft:#0F3D48; --accent-soft-bd:#134E5C;
    --good:#34D399; --good-bg:#0A2B22; --warn:#F59E0B; --warn-bg:#2A2213; --bad:#F87171; --bad-bg:#2A1414;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
  }
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);
  font:15px/1.55 "IBM Plex Sans","Segoe UI",Roboto,system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;padding:32px 20px 64px}
.wrap{max-width:1020px;margin:0 auto}
h1,h2,h3{font-family:"Space Grotesk","Segoe UI",system-ui,sans-serif;letter-spacing:-.01em;line-height:1.2}
.eyebrow{font-size:11px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:var(--accent)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow)}
/* header */
.head{display:flex;justify-content:space-between;gap:24px;align-items:center;padding:28px 32px;margin-bottom:20px;flex-wrap:wrap}
.head h1{font-size:26px;margin:6px 0 10px}
.meta{font-size:13px;color:var(--muted);line-height:1.7}
.meta code{font-family:Consolas,ui-monospace,monospace;background:var(--accent-soft);color:var(--accent-2);padding:1px 6px;border-radius:5px}
.grade{text-align:center;min-width:150px}
.grade .badge{font-family:"Space Grotesk",sans-serif;font-size:56px;font-weight:800;line-height:1;
  width:110px;height:110px;border-radius:24px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px}
.grade .score{font-size:13px;color:var(--muted)}
.g-good{background:var(--good-bg);color:var(--good)}
.g-warn{background:var(--warn-bg);color:var(--warn)}
.g-bad{background:var(--bad-bg);color:var(--bad)}
.counts{display:flex;gap:10px;justify-content:center;margin-top:10px;font-size:12px;font-weight:600}
.pill{padding:3px 10px;border-radius:999px;border:1px solid var(--line)}
.pill.err{background:var(--bad-bg);color:var(--bad);border-color:transparent}
.pill.warn{background:var(--warn-bg);color:var(--warn);border-color:transparent}
/* section */
.section{margin:28px 0 10px}
.section h2{font-size:18px}
.section p.sub{font-size:13px;color:var(--muted);margin-top:3px}
/* scorecard */
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:14px}
.dim{padding:16px 18px}
.dim .top{display:flex;justify-content:space-between;align-items:baseline}
.dim .name{font-weight:700;font-size:14px}
.dim .val{font-family:"Space Grotesk",sans-serif;font-weight:800;font-size:20px}
.dim .desc{font-size:12px;color:var(--muted);margin:6px 0 10px;min-height:32px}
.bar{height:7px;border-radius:999px;background:var(--line);overflow:hidden}
.bar > i{display:block;height:100%;border-radius:999px}
.dim .foot{font-size:11px;color:var(--faint);margin-top:7px}
.fill-good{background:var(--good)}.fill-warn{background:var(--warn)}.fill-bad{background:var(--bad)}
/* table */
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
.tablecard{overflow-x:auto;padding:8px 4px}
th,td{text-align:left;padding:9px 14px;border-bottom:1px solid var(--line);white-space:nowrap}
th{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--faint);font-weight:700}
td.num,th.num{text-align:right}
.type-tag{font-size:11px;font-weight:600;padding:2px 8px;border-radius:6px;background:var(--accent-soft);color:var(--accent-2)}
.keymark{color:var(--good);font-weight:800}
.miss-lo{color:var(--warn)}.miss-hi{color:var(--bad);font-weight:700}
/* findings */
.finding{padding:16px 18px;margin-top:12px;border-left:4px solid var(--line)}
.finding.err{border-left-color:var(--bad)}
.finding.warn{border-left-color:var(--warn)}
.finding.info{border-left-color:var(--accent)}
.finding .ftop{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.finding .ttl{font-weight:700;font-size:14px}
.tag{font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;padding:2px 8px;border-radius:999px}
.tag.err{background:var(--bad-bg);color:var(--bad)}.tag.warn{background:var(--warn-bg);color:var(--warn)}.tag.info{background:var(--accent-soft);color:var(--accent-2)}
.tag.dim{background:var(--bg);color:var(--muted);border:1px solid var(--line)}
.finding .det{font-size:13px;color:var(--muted);margin-top:6px}
.samples{margin-top:9px;display:flex;flex-wrap:wrap;gap:6px}
.samples code{font-family:Consolas,ui-monospace,monospace;font-size:12px;background:var(--bg);border:1px solid var(--line);color:var(--ink);padding:2px 7px;border-radius:6px}
.clean{padding:22px;text-align:center;color:var(--good);font-weight:600}
.foot{text-align:center;font-size:12px;color:var(--faint);margin-top:36px;line-height:1.7}
@media (max-width:720px){.grid{grid-template-columns:1fr}.head{flex-direction:column;align-items:flex-start}}
"""

_SEV_CLASS = {Severity.ERROR: "err", Severity.WARNING: "warn", Severity.INFO: "info"}
_SEV_LABEL = {Severity.ERROR: "Error", Severity.WARNING: "Warning", Severity.INFO: "Info"}


def _score_class(score: float) -> str:
    if score >= 85:
        return "good"
    if score >= 70:
        return "warn"
    return "bad"


def _head(report: QualityReport) -> str:
    src = escape(report.source)
    sheet = f" · sheet <code>{escape(report.sheet)}</code>" if report.sheet else ""
    blanks = (
        f" · {report.blank_rows_ignored} blank row(s) ignored"
        if report.blank_rows_ignored
        else ""
    )
    gclass = _score_class(report.score)
    counts = (
        f'<span class="pill err">{report.error_count} errors</span>'
        f'<span class="pill warn">{report.warning_count} warnings</span>'
    )
    return f"""
<div class="card head">
  <div>
    <div class="eyebrow">Data Quality Report</div>
    <h1>Spreadsheet Cleaner</h1>
    <div class="meta">
      Source: <code>{src}</code>{sheet}<br>
      {report.rows:,} rows · {report.cols} columns{blanks}<br>
      Generated {report.generated_at:%Y-%m-%d %H:%M} UTC · v{escape(report.tool_version)}
    </div>
  </div>
  <div class="grade">
    <div class="badge g-{gclass}">{report.grade}</div>
    <div class="score">{report.score:.0f} / 100</div>
    <div class="counts">{counts}</div>
  </div>
</div>"""


def _scorecard(report: QualityReport) -> str:
    cards = []
    for dim in DIMENSION_ORDER:
        stat = report.stat(dim)
        cls = _score_class(stat.score)
        denom = (
            f"{stat.affected:,} of {stat.applicable:,} checked"
            if stat.applicable
            else "not applicable"
        )
        cards.append(f"""
    <div class="card dim">
      <div class="top"><span class="name">{dim.label}</span><span class="val">{stat.score:.0f}</span></div>
      <div class="desc">{escape(dim.description)}</div>
      <div class="bar"><i class="fill-{cls}" style="width:{stat.score:.0f}%"></i></div>
      <div class="foot">{denom}</div>
    </div>""")
    return f"""
<div class="section"><h2>Quality by dimension</h2>
<p class="sub">Each score is the share of checked values that passed. Dimensions follow the DAMA data-quality framework.</p></div>
<div class="grid">{"".join(cards)}</div>"""


def _columns(report: QualityReport) -> str:
    rows = []
    for c in report.columns:
        if c.missing == 0:
            miss = "0"
        elif c.missing / c.total < 0.2:
            miss = f'<span class="miss-lo">{c.missing}</span>'
        else:
            miss = f'<span class="miss-hi">{c.missing}</span>'
        key = '<span class="keymark">✓</span>' if c.is_unique else ""
        rows.append(f"""
    <tr>
      <td>{escape(c.name)}</td>
      <td><span class="type-tag">{c.inferred_type}</span></td>
      <td class="num">{c.fill_rate:.0%}</td>
      <td class="num">{miss}</td>
      <td class="num">{c.distinct:,}</td>
      <td style="text-align:center">{key}</td>
    </tr>""")
    return f"""
<div class="section"><h2>Columns</h2></div>
<div class="card tablecard">
<table>
  <thead><tr>
    <th>Column</th><th>Inferred type</th><th class="num">Fill</th>
    <th class="num">Missing</th><th class="num">Distinct</th><th style="text-align:center">Unique key</th>
  </tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table></div>"""


def _findings(report: QualityReport) -> str:
    issues = report.sorted_issues()
    if not issues:
        return (
            '<div class="section"><h2>Findings</h2></div>'
            '<div class="card clean">✓ No issues found. This table looks clean.</div>'
        )
    blocks = []
    for issue in issues:
        sev = _SEV_CLASS[issue.severity]
        samples = ""
        if issue.samples:
            chips = "".join(f"<code>{escape(str(s))}</code>" for s in issue.samples)
            samples = f'<div class="samples">{chips}</div>'
        col = f'<span class="tag dim">{escape(issue.column)}</span>' if issue.column else ""
        blocks.append(f"""
<div class="card finding {sev}">
  <div class="ftop">
    <span class="tag {sev}">{_SEV_LABEL[issue.severity]}</span>
    <span class="tag dim">{issue.dimension.label}</span>
    {col}
    <span class="ttl">{escape(issue.title)}</span>
  </div>
  <div class="det">{escape(issue.detail)}</div>
  {samples}
</div>""")
    return f'<div class="section"><h2>Findings</h2><p class="sub">Most severe first.</p></div>{"".join(blocks)}'


def to_html(report: QualityReport) -> str:
    body = _head(report) + _scorecard(report) + _columns(report) + _findings(report)
    foot = (
        '<div class="foot">Generated by Spreadsheet Cleaner. Fully offline. '
        "Your data never left this machine.<br>"
        "This report profiles the source file; it does not modify it.</div>"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data Quality Report - Spreadsheet Cleaner</title>
<style>{_CSS}</style>
</head>
<body><div class="wrap">{body}{foot}</div></body>
</html>"""
