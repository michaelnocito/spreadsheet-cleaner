"""Render a ValidationReport ("will it load?") as HTML or Markdown."""

from __future__ import annotations

from html import escape

from spreadsheet_cleaner.core.models import VALIDATION_ORDER, Severity
from spreadsheet_cleaner.report.html import _CSS, _SEV_CLASS, _SEV_LABEL, _score_class
from spreadsheet_cleaner.validate.dedupe import DedupeResult
from spreadsheet_cleaner.validate.rules import ValidationReport


def _verdict(report: ValidationReport) -> tuple[str, str]:
    if report.passed:
        return "PASS", "good"
    return "FAIL", "bad"


def to_html(report: ValidationReport, dedupe: DedupeResult | None = None) -> str:
    verdict, vclass = _verdict(report)
    counts = (
        f'<span class="pill err">{report.error_count} errors</span>'
        f'<span class="pill warn">{report.warning_count} warnings</span>'
    )
    sheet = f" · sheet <code>{escape(report.sheet)}</code>" if report.sheet else ""
    schema = (
        f"<br>Target schema: <code>{escape(report.schema_path)}</code>"
        if report.schema_path
        else ""
    )
    head = f"""
<div class="card head">
  <div>
    <div class="eyebrow">Validation Report - Will It Load?</div>
    <h1>{escape(report.target)}</h1>
    <div class="meta">
      Source: <code>{escape(report.source)}</code>{sheet}{schema}<br>
      {report.rows:,} rows · {len(report.fields)} target field(s)<br>
      Generated {report.generated_at:%Y-%m-%d %H:%M} UTC · v{escape(report.tool_version)}
    </div>
  </div>
  <div class="grade">
    <div class="badge g-{vclass}" style="font-size:34px">{verdict}</div>
    <div class="score">{report.score:.0f} / 100</div>
    <div class="counts">{counts}</div>
  </div>
</div>"""

    cards = []
    for dim in VALIDATION_ORDER:
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
    scorecard = f"""
<div class="section"><h2>Checks by dimension</h2>
<p class="sub">Scores measure the share of checked values that satisfy the target's contract.</p></div>
<div class="grid">{"".join(cards)}</div>"""

    rows = []
    for f in report.fields:
        if not f.found:
            status = '<span class="tag err">not found</span>'
        elif f.errors:
            status = f'<span class="tag err">{f.errors} error(s)</span>'
        elif f.warnings:
            status = f'<span class="tag warn">{f.warnings} warning(s)</span>'
        else:
            status = '<span class="keymark">&#10003; ok</span>'
        rows.append(f"""
    <tr>
      <td>{escape(f.name)}</td>
      <td><code>{escape(f.source)}</code></td>
      <td style="text-align:center">{status}</td>
    </tr>""")
    mapping = f"""
<div class="section"><h2>Field mapping</h2></div>
<div class="card tablecard">
<table>
  <thead><tr><th>Target field</th><th>Source column</th><th style="text-align:center">Status</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table></div>"""

    issues = report.sorted_issues()
    if issues:
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
        findings = f'<div class="section"><h2>Findings</h2><p class="sub">Most severe first.</p></div>{"".join(blocks)}'
    else:
        findings = (
            '<div class="section"><h2>Findings</h2></div>'
            '<div class="card clean">&#10003; Every check passed. This file satisfies the target contract.</div>'
        )

    dedupe_html = ""
    if dedupe is not None:
        if dedupe.skipped:
            body = f'<div class="card finding info"><div class="det">{escape(dedupe.skip_reason)}</div></div>'
        elif dedupe.pairs:
            pair_rows = "".join(
                f"<tr><td class='num'>{p.row_a}</td><td class='num'>{p.row_b}</td>"
                f"<td class='num'>{p.similarity:.0%}</td>"
                f"<td>{escape(p.preview_a)}</td><td>{escape(p.preview_b)}</td></tr>"
                for p in dedupe.pairs[:50]
            )
            more = (
                f"<p class='sub'>Showing 50 of {len(dedupe.pairs)} pair(s).</p>"
                if len(dedupe.pairs) > 50
                else ""
            )
            body = f"""{more}<div class="card tablecard"><table>
  <thead><tr><th class="num">Row</th><th class="num">Row</th><th class="num">Similarity</th><th>Record</th><th>Record</th></tr></thead>
  <tbody>{pair_rows}</tbody></table></div>"""
        else:
            body = '<div class="card clean">&#10003; No near-duplicate rows found.</div>'
        dedupe_html = (
            f'<div class="section"><h2>Near-duplicates</h2>'
            f'<p class="sub">Rows that are almost the same record - review before load '
            f'({dedupe.rows_checked:,} row(s) scanned).</p></div>{body}'
        )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Validation Report - Spreadsheet Cleaner</title>
<style>{_CSS}</style></head>
<body><div class="wrap">
{head}{scorecard}{mapping}{findings}{dedupe_html}
<div class="foot">Generated by Spreadsheet Cleaner. Fully offline. Your data never left this machine.</div>
</div></body></html>"""


def to_markdown(report: ValidationReport, dedupe: DedupeResult | None = None) -> str:
    verdict, _ = _verdict(report)
    lines = [
        "# Validation Report - Will It Load?",
        "",
        f"**Verdict: {verdict}** ({report.score:.0f}/100)",
        "",
        f"**Source:** `{report.source}`",
        f"**Target:** {report.target}"
        + (f" (schema `{report.schema_path}`)" if report.schema_path else ""),
        f"**Generated:** {report.generated_at:%Y-%m-%d %H:%M UTC}",
        f"**Rows:** {report.rows:,} · {report.error_count} error(s) · {report.warning_count} warning(s)",
        "",
        "## Field mapping",
        "",
        "| Target field | Source column | Status |",
        "|---|---|---|",
    ]
    for f in report.fields:
        if not f.found:
            status = "not found"
        elif f.errors:
            status = f"{f.errors} error(s)"
        elif f.warnings:
            status = f"{f.warnings} warning(s)"
        else:
            status = "ok"
        lines.append(f"| {f.name} | `{f.source}` | {status} |")
    lines += ["", "## Findings", ""]
    issues = report.sorted_issues()
    if not issues:
        lines.append("Every check passed. This file satisfies the target contract.")
    for issue in issues:
        mark = {Severity.ERROR: "ERROR", Severity.WARNING: "WARN", Severity.INFO: "INFO"}[issue.severity]
        lines.append(f"- **[{mark}] {issue.title}** ({issue.dimension.label}) - {issue.detail}")
        if issue.samples:
            lines.append(f"  Examples: {', '.join(f'`{s}`' for s in issue.samples)}")
    if dedupe is not None:
        lines += ["", "## Near-duplicates", ""]
        if dedupe.skipped:
            lines.append(dedupe.skip_reason)
        elif not dedupe.pairs:
            lines.append("No near-duplicate rows found.")
        else:
            for p in dedupe.pairs[:50]:
                lines.append(
                    f"- rows {p.row_a} and {p.row_b} ({p.similarity:.0%}): "
                    f"`{p.preview_a}` vs `{p.preview_b}`"
                )
    return "\n".join(lines)
