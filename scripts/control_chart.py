#!/usr/bin/env python3
"""
control_chart.py - Statistical process control over per-run JSONs.

NEW in pre-release-review v5.1 (1J).

Reads .local/pre-release-review/runs/*.json from a project and computes
I-MR (Individuals + Moving Range), u-chart, g-chart, and DPMO summaries
over time. Text-output only (no graphical dependency) for portability.

Use cases:
  - I-MR over `tag_to_publish_seconds`: detect drift in release pipeline duration
  - u-chart over findings/release: detect rising defect rate (defects normalized by opportunities)
  - g-chart over `bypass_events[]`: detect decreasing gap between protocol bypasses
  - DPMO: per-million opportunity rate as a single quality KPI

Conventions:
  - 3-sigma control limits (UCL/LCL) per ASTM standard
  - At least 8 data points required for limit estimation (rule of thumb;
    < 8 points produces unreliable limits and is flagged with WARN)
  - "Out of control" rules per Western Electric (single point > 3-sigma is
    flagged; runs of 8 same-side points flagged as drift)

Stdlib only; no numpy/pandas dependency. Cross-platform.

Usage:
    python ~/.claude/skills/pre-release-review/scripts/control_chart.py \\
        --chart imr --metric tag_to_publish_seconds

    python ~/.claude/skills/pre-release-review/scripts/control_chart.py \\
        --chart u --defects findings_count --opportunities commits_count

    python ~/.claude/skills/pre-release-review/scripts/control_chart.py \\
        --chart g --event-list bypass_events

    python ~/.claude/skills/pre-release-review/scripts/control_chart.py \\
        --chart dpmo --defects findings_count --opportunities commits_count
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


# ---------- IO ----------

def load_runs(runs_dir: Path) -> list[dict[str, Any]]:
    """Load all per-run JSONs sorted by completed_at (ascending)."""
    if not runs_dir.exists():
        sys.exit(f"ERROR: runs directory not found: {runs_dir}")
    files = sorted(runs_dir.glob("*.json"))
    if not files:
        sys.exit(f"ERROR: no JSON files in {runs_dir}")
    runs = []
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"WARN: skipping malformed JSON {f.name}: {e}", file=sys.stderr)
            continue
        d.setdefault("_path", str(f))
        runs.append(d)
    runs.sort(key=lambda r: r.get("completed_at", ""))
    return runs


def get_nested(d: dict[str, Any], dotted_key: str) -> Any:
    """Resolve 'a.b.c' against a nested dict. Returns None if missing."""
    cur: Any = d
    for k in dotted_key.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


# ---------- I-MR (Individuals + Moving Range) ----------

def imr_chart(runs: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    """Compute I-MR control chart for a continuous metric.

    Returns dict with: values, moving_ranges, x_bar, mr_bar, i_ucl, i_lcl,
    mr_ucl, out_of_control[].
    """
    values: list[float] = []
    labels: list[str] = []
    for r in runs:
        v = get_nested(r, metric)
        if v is None:
            continue
        try:
            values.append(float(v))
        except (TypeError, ValueError):
            continue
        labels.append(r.get("run_id", r.get("_path", "?"))[:24])

    if len(values) < 2:
        return {"error": f"Need >= 2 points; got {len(values)}"}

    # Moving ranges (absolute diffs of consecutive points)
    mrs = [abs(values[i] - values[i - 1]) for i in range(1, len(values))]
    x_bar = sum(values) / len(values)
    mr_bar = sum(mrs) / len(mrs) if mrs else 0.0

    # 3-sigma I-MR limits, ASTM constants:
    # I-chart: UCL = x_bar + 2.66 * mr_bar; LCL = x_bar - 2.66 * mr_bar
    # MR-chart: UCL = 3.267 * mr_bar; LCL = 0
    i_ucl = x_bar + 2.66 * mr_bar
    i_lcl = x_bar - 2.66 * mr_bar
    mr_ucl = 3.267 * mr_bar

    out_of_control: list[dict[str, Any]] = []
    for i, v in enumerate(values):
        if v > i_ucl or v < i_lcl:
            out_of_control.append({"index": i, "label": labels[i], "value": v,
                                   "rule": "I-chart point outside 3-sigma"})
    for i, mr in enumerate(mrs, start=1):
        if mr > mr_ucl:
            out_of_control.append({"index": i, "label": labels[i], "value": mr,
                                   "rule": "MR-chart point above UCL"})

    # Western Electric rule 1c: 8 consecutive points same side of centerline
    above = 0
    below = 0
    for i, v in enumerate(values):
        if v > x_bar:
            above += 1
            below = 0
        elif v < x_bar:
            below += 1
            above = 0
        else:
            above = below = 0
        if above >= 8:
            out_of_control.append({"index": i, "label": labels[i], "value": v,
                                   "rule": "8 consecutive points above x-bar (drift up)"})
        if below >= 8:
            out_of_control.append({"index": i, "label": labels[i], "value": v,
                                   "rule": "8 consecutive points below x-bar (drift down)"})

    return {
        "chart": "I-MR",
        "metric": metric,
        "n": len(values),
        "values": values,
        "labels": labels,
        "moving_ranges": mrs,
        "x_bar": x_bar,
        "mr_bar": mr_bar,
        "i_ucl": i_ucl,
        "i_lcl": i_lcl,
        "mr_ucl": mr_ucl,
        "out_of_control": out_of_control,
        "stability": "in-control" if not out_of_control else "out-of-control",
    }


# ---------- u-chart (defects per unit, variable opportunity) ----------

def u_chart(runs: list[dict[str, Any]], defects_key: str,
            opps_key: str) -> dict[str, Any]:
    """Compute u-chart for defect rate normalized by opportunity count.

    Each subgroup has a variable opportunity size (commits per release,
    LOC changed, etc.); u-chart has different UCL/LCL per subgroup.
    """
    rows: list[tuple[str, float, float]] = []
    for r in runs:
        d = get_nested(r, defects_key)
        o = get_nested(r, opps_key)
        if d is None or o is None:
            continue
        try:
            d = float(d)
            o = float(o)
        except (TypeError, ValueError):
            continue
        if o <= 0:
            continue
        rows.append((r.get("run_id", r.get("_path", "?"))[:24], d, o))

    if len(rows) < 2:
        return {"error": f"Need >= 2 points; got {len(rows)}"}

    labels = [r[0] for r in rows]
    defects = [r[1] for r in rows]
    opps = [r[2] for r in rows]

    total_defects = sum(defects)
    total_opps = sum(opps)
    u_bar = total_defects / total_opps

    out_of_control: list[dict[str, Any]] = []
    per_point: list[dict[str, Any]] = []
    for i, (label, d, o) in enumerate(rows):
        u_i = d / o
        # Variable UCL/LCL based on subgroup size
        sigma = math.sqrt(u_bar / o)
        ucl_i = u_bar + 3 * sigma
        lcl_i = max(0.0, u_bar - 3 * sigma)
        per_point.append({"label": label, "u_i": u_i, "ucl": ucl_i, "lcl": lcl_i,
                          "defects": d, "opportunities": o})
        if u_i > ucl_i or u_i < lcl_i:
            out_of_control.append({"index": i, "label": label, "value": u_i,
                                   "rule": f"u-chart point outside [{lcl_i:.4f}, {ucl_i:.4f}]"})

    return {
        "chart": "u-chart",
        "defects_key": defects_key,
        "opportunities_key": opps_key,
        "n": len(rows),
        "u_bar": u_bar,
        "total_defects": total_defects,
        "total_opportunities": total_opps,
        "per_point": per_point,
        "out_of_control": out_of_control,
        "stability": "in-control" if not out_of_control else "out-of-control",
    }


# ---------- g-chart (between-event opportunities) ----------

def g_chart(runs: list[dict[str, Any]], event_list_key: str) -> dict[str, Any]:
    """Compute g-chart for between-event counts.

    Counts opportunities (runs) between successive events. Useful for
    rare events like protocol bypasses.
    """
    gaps: list[int] = []
    cur_gap = 0
    last_event_run: str | None = None
    event_runs: list[str] = []
    for r in runs:
        events = get_nested(r, event_list_key) or []
        if events:
            if last_event_run is not None:
                gaps.append(cur_gap)
            last_event_run = r.get("run_id", r.get("_path", "?"))[:24]
            event_runs.append(last_event_run)
            cur_gap = 0
        else:
            cur_gap += 1

    if len(gaps) < 2:
        return {"error": f"Need >= 2 inter-event gaps; got {len(gaps)} "
                         f"(events seen: {len(event_runs)})"}

    g_bar = sum(gaps) / len(gaps)
    # g-chart UCL approximation: g_bar + 3 * sqrt(g_bar * (g_bar + 1))
    g_ucl = g_bar + 3 * math.sqrt(g_bar * (g_bar + 1))
    g_lcl = max(0.0, g_bar - 3 * math.sqrt(g_bar * (g_bar + 1)))

    out_of_control: list[dict[str, Any]] = []
    for i, gap in enumerate(gaps):
        if gap > g_ucl:
            out_of_control.append({"index": i, "gap": gap,
                                   "rule": f"gap above UCL ({g_ucl:.2f})"})
        if gap < g_lcl:
            out_of_control.append({"index": i, "gap": gap,
                                   "rule": f"gap below LCL ({g_lcl:.2f})"})

    return {
        "chart": "g-chart",
        "event_list_key": event_list_key,
        "n_gaps": len(gaps),
        "n_events": len(event_runs),
        "gaps": gaps,
        "event_runs": event_runs,
        "g_bar": g_bar,
        "g_ucl": g_ucl,
        "g_lcl": g_lcl,
        "out_of_control": out_of_control,
        "stability": "in-control" if not out_of_control else "out-of-control",
    }


# ---------- DPMO (Defects Per Million Opportunities) ----------

def dpmo(runs: list[dict[str, Any]], defects_key: str,
         opps_key: str) -> dict[str, Any]:
    """Compute DPMO as the single Six-Sigma quality KPI.

    Six-Sigma DPMO benchmarks:
      6-sigma: 3.4 DPMO
      5-sigma: 233 DPMO
      4-sigma: 6,210 DPMO
      3-sigma: 66,807 DPMO
      2-sigma: 308,538 DPMO
    """
    total_defects = 0.0
    total_opps = 0.0
    for r in runs:
        d = get_nested(r, defects_key)
        o = get_nested(r, opps_key)
        if d is None or o is None:
            continue
        try:
            total_defects += float(d)
            total_opps += float(o)
        except (TypeError, ValueError):
            continue

    if total_opps <= 0:
        return {"error": "Total opportunities <= 0"}

    dpmo_value = (total_defects / total_opps) * 1_000_000
    if dpmo_value <= 3.4:
        sigma_level = "6-sigma"
    elif dpmo_value <= 233:
        sigma_level = "5-sigma"
    elif dpmo_value <= 6210:
        sigma_level = "4-sigma"
    elif dpmo_value <= 66807:
        sigma_level = "3-sigma"
    elif dpmo_value <= 308538:
        sigma_level = "2-sigma"
    else:
        sigma_level = "< 2-sigma"

    return {
        "chart": "DPMO",
        "defects_key": defects_key,
        "opportunities_key": opps_key,
        "total_defects": total_defects,
        "total_opportunities": total_opps,
        "dpmo": dpmo_value,
        "sigma_level": sigma_level,
    }


# ---------- Output formatting ----------

def render_text(result: dict[str, Any]) -> str:
    """Human-readable text output."""
    if "error" in result:
        return f"ERROR: {result['error']}"

    lines = [
        "",
        "=" * 60,
        f"  {result['chart']}",
        "=" * 60,
    ]

    chart = result["chart"]
    if chart == "I-MR":
        lines.append(f"  Metric:           {result['metric']}")
        lines.append(f"  N points:         {result['n']}")
        lines.append(f"  x-bar:            {result['x_bar']:.3f}")
        lines.append(f"  MR-bar:           {result['mr_bar']:.3f}")
        lines.append(f"  I-chart UCL:      {result['i_ucl']:.3f}")
        lines.append(f"  I-chart LCL:      {result['i_lcl']:.3f}")
        lines.append(f"  MR-chart UCL:     {result['mr_ucl']:.3f}")
        lines.append(f"  Stability:        {result['stability'].upper()}")
        if result.get("n", 0) < 8:
            lines.append("  WARN: < 8 points; limits unreliable")

    elif chart == "u-chart":
        lines.append(f"  Defects key:      {result['defects_key']}")
        lines.append(f"  Opps key:         {result['opportunities_key']}")
        lines.append(f"  N subgroups:      {result['n']}")
        lines.append(f"  u-bar:            {result['u_bar']:.6f}")
        lines.append(f"  Total defects:    {result['total_defects']}")
        lines.append(f"  Total opps:       {result['total_opportunities']}")
        lines.append(f"  Stability:        {result['stability'].upper()}")

    elif chart == "g-chart":
        lines.append(f"  Event list key:   {result['event_list_key']}")
        lines.append(f"  N events:         {result['n_events']}")
        lines.append(f"  N inter-event gaps: {result['n_gaps']}")
        lines.append(f"  g-bar (mean gap): {result['g_bar']:.3f} runs between events")
        lines.append(f"  g-chart UCL:      {result['g_ucl']:.3f}")
        lines.append(f"  g-chart LCL:      {result['g_lcl']:.3f}")
        lines.append(f"  Stability:        {result['stability'].upper()}")

    elif chart == "DPMO":
        lines.append(f"  Defects key:      {result['defects_key']}")
        lines.append(f"  Opps key:         {result['opportunities_key']}")
        lines.append(f"  Total defects:    {result['total_defects']}")
        lines.append(f"  Total opps:       {result['total_opportunities']}")
        lines.append(f"  DPMO:             {result['dpmo']:.1f}")
        lines.append(f"  Sigma level:      {result['sigma_level']}")

    if result.get("out_of_control"):
        lines.append("")
        lines.append("  Out-of-control signals:")
        for sig in result["out_of_control"][:20]:
            lines.append(f"    - {sig.get('label', sig.get('index'))}: "
                         f"{sig.get('value', sig.get('gap'))} ({sig['rule']})")
        extra = len(result["out_of_control"]) - 20
        if extra > 0:
            lines.append(f"    ... and {extra} more signals (truncated)")

    lines.append("")
    return "\n".join(lines)


# ---------- CLI ----------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Statistical process control over per-run JSONs (v5.1 1J)",
        epilog="See ~/.claude/skills/pre-release-review/scripts/control_chart.py docstring for examples.",
    )
    p.add_argument("--chart", required=True,
                   choices=["imr", "u", "g", "dpmo"],
                   help="Chart type to compute")
    p.add_argument("--metric", help="Metric path (dotted) for I-MR (e.g., tag_to_publish_seconds)")
    p.add_argument("--defects", help="Defects metric path (u-chart, DPMO)")
    p.add_argument("--opportunities", help="Opportunities metric path (u-chart, DPMO)")
    p.add_argument("--event-list", help="Event-list field path (g-chart, e.g., bypass_events)")
    p.add_argument("--runs-dir", default=".local/pre-release-review/runs",
                   help="Per-run JSON directory (default: .local/pre-release-review/runs)")
    p.add_argument("--json", action="store_true",
                   help="Output JSON instead of human-readable text")
    args = p.parse_args()

    runs = load_runs(Path(args.runs_dir))

    if args.chart == "imr":
        if not args.metric:
            sys.exit("ERROR: --chart imr requires --metric")
        result = imr_chart(runs, args.metric)
    elif args.chart == "u":
        if not (args.defects and args.opportunities):
            sys.exit("ERROR: --chart u requires --defects and --opportunities")
        result = u_chart(runs, args.defects, args.opportunities)
    elif args.chart == "g":
        if not args.event_list:
            sys.exit("ERROR: --chart g requires --event-list")
        result = g_chart(runs, args.event_list)
    elif args.chart == "dpmo":
        if not (args.defects and args.opportunities):
            sys.exit("ERROR: --chart dpmo requires --defects and --opportunities")
        result = dpmo(runs, args.defects, args.opportunities)
    else:
        sys.exit(f"ERROR: unknown chart: {args.chart}")

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(render_text(result))

    # Exit code: 0 if in-control, 1 if out-of-control, 2 if error
    if "error" in result:
        return 2
    if result.get("stability") == "out-of-control":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
