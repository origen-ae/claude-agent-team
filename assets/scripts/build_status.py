#!/usr/bin/env python3
"""
Scan the frontmatter of all PRDs, aggregate the stage of multiple documents by
requirement ID, and generate STATUS.md and status.html.
"""
import sys
import yaml
import frontmatter
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Make emoji/UTF-8 output safe on consoles with a non-UTF-8 default encoding
# (e.g. Windows GBK). No-op if reconfigure is unavailable or fails.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).parent.parent
DOCS_ROOT = ROOT / "docs"
STATUS_MD = ROOT / "STATUS.md"
STATUS_HTML = ROOT / "status.html"

# Stage definitions (order, emoji, display name)
STAGES = [
    ("pending", "⚪", "Pending"),
    ("pm-designing", "🟦", "PM designing"),
    ("awaiting-prd-approval", "🟡", "Awaiting PRD approval"),
    ("architect-designing", "🟪", "Architecture design"),
    ("awaiting-spec-approval", "🟡", "Awaiting SPEC approval"),
    ("developing", "🟧", "Developing"),
    ("testing-round1", "🟨", "Testing (round 1)"),
    ("fixing", "🔴", "Fixing"),
    ("testing-round2", "🟨", "Retesting (round 2)"),
    ("awaiting-deploy-approval", "🟡", "Awaiting deploy approval"),
    ("deployed", "✅", "Deployed"),
    ("cancelled", "❌", "Cancelled"),
    ("superseded", "🔁", "Superseded"),
]
STAGE_LABEL = {k: (icon, label) for k, icon, label in STAGES}
STAGE_ORDER = {k: i for i, (k, _, _) in enumerate(STAGES)}


def load_backlog():
    """Parse docs/backlog.md and return list of backlog items."""
    backlog_path = DOCS_ROOT / "backlog.md"
    if not backlog_path.exists():
        return []
    items = []
    import re
    pattern = re.compile(
        r"\|\s*(BACKLOG-\d+)\s*\|\s*([^|]+?)\s*\|\s*(P[012])\s*\|\s*([^|]*?)\s*\|\s*(open|in-progress|done|wontfix|superseded|resolved)\s*\|",
        re.IGNORECASE,
    )
    try:
        text = backlog_path.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            items.append({
                "id": m.group(1),
                "title": m.group(2).strip(),
                "priority": m.group(3).upper(),
                "source": m.group(4).strip(),
                "status": m.group(5).lower(),
            })
    except Exception as e:
        print(f"⚠️  Could not parse backlog.md: {e}", file=sys.stderr)
    return items


def load_all_docs():
    """Load the frontmatter of all markdown documents"""
    docs = []
    for md_file in DOCS_ROOT.rglob("*.md"):
        if md_file.name in ("README.md", "index.yaml", "backlog.md"):
            continue
        if "_templates" in md_file.parts:
            continue
        try:
            post = frontmatter.load(md_file)
            fm = post.metadata
            if "id" not in fm:
                continue
            docs.append({
                "id": fm["id"],
                "title": fm.get("title", ""),
                "type": fm.get("type", "unknown"),
                "stage": fm.get("stage", "unknown"),
                "owner": fm.get("owner", ""),
                "updated": str(fm.get("updated", "")),
                "summary": fm.get("summary", "").strip(),
                "path": str(md_file.relative_to(ROOT)),
                "priority": fm.get("priority", ""),
            })
        except Exception as e:
            print(f"⚠️  Skipping {md_file.name}: {e}", file=sys.stderr)
    return docs


def extract_req_id(doc_id):
    """Extract requirement number 008 from PRD-008 / SPEC-008 / TEST-PLAN-008"""
    parts = doc_id.split("-")
    if len(parts) >= 2 and parts[0] in ("PRD", "SPEC", "TEST"):
        # TEST-PLAN-008 → 008
        if parts[0] == "TEST" and len(parts) >= 3:
            return parts[-1]
        return parts[-1]
    return None


def group_by_requirement(docs):
    """Aggregate by requirement number"""
    groups = defaultdict(dict)
    for doc in docs:
        req_id = extract_req_id(doc["id"])
        if not req_id:
            continue
        # Skip SPEC-000 (project baseline of the current state)
        if doc["id"] == "SPEC-000":
            continue
        if doc["type"] == "prd":
            groups[req_id]["prd"] = doc
        elif doc["type"] == "spec":
            groups[req_id]["spec"] = doc
        elif doc["type"] == "test-plan":
            groups[req_id]["test-plan"] = doc
    return groups


def get_canonical_stage(group):
    """Determine the authoritative stage from a requirement's multiple documents (take the PRD's stage)"""
    if "prd" in group:
        return group["prd"]["stage"]
    if "spec" in group:
        return group["spec"]["stage"]
    return "unknown"


def get_stage_progress(group):
    """Return the completion status of each stage for this requirement"""
    prd_stage = get_canonical_stage(group)
    current_idx = STAGE_ORDER.get(prd_stage, -1)

    # Simplified progress display: based on the current stage, infer that all preceding stages are complete
    progress = []
    milestones = [
        ("pm-designing", "PM design"),
        ("awaiting-prd-approval", "PRD approval"),
        ("architect-designing", "Architecture"),
        ("awaiting-spec-approval", "SPEC approval"),
        ("developing", "Develop"),
        ("testing-round1", "Test 1"),
        ("testing-round2", "Test 2"),
        ("awaiting-deploy-approval", "Deploy approval"),
        ("deployed", "Deploy"),
    ]
    for stage_key, label in milestones:
        idx = STAGE_ORDER[stage_key]
        if idx < current_idx:
            progress.append(("✅", label))
        elif idx == current_idx:
            icon, _ = STAGE_LABEL[stage_key]
            progress.append((icon, label))
        else:
            progress.append(("⚪", label))
    return progress


def render_markdown(groups):
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"# Project Status Board\n")
    lines.append(f"> Last updated: {now}\n")
    lines.append("---\n")

    # Overview
    all_stages = defaultdict(int)
    for g in groups.values():
        s = get_canonical_stage(g)
        all_stages[s] += 1

    lines.append("## Overview\n")
    lines.append(f"**Total requirements**: {len(groups)}\n")

    summary_items = []
    for stage_key, icon, label in STAGES:
        count = all_stages.get(stage_key, 0)
        if count > 0:
            summary_items.append(f"- {icon} {label}: {count}")
    lines.extend(summary_items)
    lines.append("")

    # Awaiting approval (what needs your attention most)
    awaiting = [
        (rid, g) for rid, g in groups.items()
        if get_canonical_stage(g).startswith("awaiting-")
    ]
    if awaiting:
        lines.append("## 🛑 Awaiting your approval\n")
        lines.append("| ID | Title | Waiting for | Waiting since |")
        lines.append("|---|---|---|---|")
        for rid, g in awaiting:
            prd = g.get("prd", {})
            stage = get_canonical_stage(g)
            _, label = STAGE_LABEL.get(stage, ("⚪", stage))
            lines.append(
                f"| PRD-{rid} | {prd.get('title', '')} | {label} | {prd.get('updated', '')} |"
            )
        lines.append("")

    # Currently in progress
    in_progress = [
        (rid, g) for rid, g in groups.items()
        if get_canonical_stage(g) not in ("deployed", "cancelled", "pending")
        and not get_canonical_stage(g).startswith("awaiting-")
    ]
    if in_progress:
        lines.append("## 🔄 In progress\n")
        lines.append("| ID | Title | Current stage | Owner | Updated |")
        lines.append("|---|---|---|---|---|")
        for rid, g in in_progress:
            prd = g.get("prd", {})
            stage = get_canonical_stage(g)
            icon, label = STAGE_LABEL.get(stage, ("⚪", stage))
            # The currently responsible agent comes from the document of the latest stage
            current_doc = g.get("test-plan") if "testing" in stage else (
                g.get("spec") if "architect" in stage or "develop" in stage else g.get("prd")
            )
            owner = current_doc.get("owner", "") if current_doc else ""
            lines.append(
                f"| PRD-{rid} | {prd.get('title', '')} | {icon} {label} | {owner} | {prd.get('updated', '')} |"
            )
        lines.append("")

    # Details (one section per requirement)
    lines.append("## 📋 Details\n")
    sorted_reqs = sorted(
        groups.items(),
        key=lambda x: (
            STAGE_ORDER.get(get_canonical_stage(x[1]), 999),
            x[0]
        )
    )
    for rid, g in sorted_reqs:
        prd = g.get("prd", {})
        stage = get_canonical_stage(g)
        icon, label = STAGE_LABEL.get(stage, ("⚪", stage))

        lines.append(f"### {icon} PRD-{rid}: {prd.get('title', '')}\n")
        lines.append(f"**Status**: {label}")
        if prd.get("priority"):
            lines.append(f"  | **Priority**: {prd['priority']}")
        lines.append(f"  | **Last updated**: {prd.get('updated', '')}\n")

        if prd.get("summary"):
            lines.append(f"> {prd['summary']}\n")

        # Progress bar
        progress = get_stage_progress(g)
        progress_str = "  ".join([f"{ico} {lbl}" for ico, lbl in progress])
        lines.append(f"**Progress**: {progress_str}\n")

        # Related document links
        lines.append("**Related docs**:")
        if "prd" in g:
            lines.append(f"- [PRD-{rid}]({g['prd']['path']})")
        if "spec" in g:
            lines.append(f"- [SPEC-{rid}]({g['spec']['path']})")
        if "test-plan" in g:
            lines.append(f"- [TEST-PLAN-{rid}]({g['test-plan']['path']})")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Completed
    completed = [
        (rid, g) for rid, g in groups.items()
        if get_canonical_stage(g) == "deployed"
    ]
    if completed:
        lines.append("## ✅ Completed\n")
        lines.append("| ID | Title | Completed on |")
        lines.append("|---|---|---|")
        for rid, g in sorted(completed, key=lambda x: x[1].get("prd", {}).get("updated", ""), reverse=True)[:10]:
            prd = g.get("prd", {})
            lines.append(f"| PRD-{rid} | {prd.get('title', '')} | {prd.get('updated', '')} |")
        lines.append("")

    # Cancelled / Superseded
    closed = [
        (rid, g) for rid, g in groups.items()
        if get_canonical_stage(g) in ("cancelled", "superseded")
    ]
    if closed:
        lines.append("## ❌ Cancelled / 🔁 Superseded\n")
        for rid, g in closed:
            prd = g.get("prd", {})
            stage = get_canonical_stage(g)
            icon = "❌" if stage == "cancelled" else "🔁"
            lines.append(f"- {icon} PRD-{rid}: {prd.get('title', '')}")
        lines.append("")

    # Backlog summary
    backlog = load_backlog()
    open_items = [b for b in backlog if b["status"] == "open"]
    if open_items:
        lines.append("## 📥 Backlog\n")
        p0 = [b for b in open_items if b["priority"] == "P0"]
        p1 = [b for b in open_items if b["priority"] == "P1"]
        p2 = [b for b in open_items if b["priority"] == "P2"]
        lines.append(f"**Open**: {len(open_items)} items — P0: {len(p0)}  P1: {len(p1)}  P2: {len(p2)}\n")
        if p0 or p1:
            lines.append("| ID | Title | Priority | Source |")
            lines.append("|---|---|---|---|")
            for b in p0 + p1:
                lines.append(f"| {b['id']} | {b['title']} | {b['priority']} | {b['source']} |")
            lines.append("")

    return "\n".join(lines)


def render_html(groups):
    """Generate a nicer HTML status board"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Statistics
    all_stages = defaultdict(int)
    for g in groups.values():
        s = get_canonical_stage(g)
        all_stages[s] += 1

    total = len(groups)
    awaiting_count = sum(all_stages[s] for s in all_stages if s.startswith("awaiting-"))
    in_progress_count = sum(
        all_stages[s] for s in all_stages
        if s not in ("deployed", "cancelled", "pending") and not s.startswith("awaiting-")
    )
    done_count = all_stages.get("deployed", 0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Project Status Board</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif; max-width: 1200px; margin: 20px auto; padding: 20px; background: #f5f6fa; color: #2f3640; }}
  h1 {{ margin-bottom: 5px; }}
  .meta {{ color: #718093; font-size: 14px; margin-bottom: 30px; }}
  .summary {{ display: flex; gap: 20px; margin-bottom: 30px; }}
  .card {{ flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; }}
  .card .num {{ font-size: 36px; font-weight: bold; }}
  .card .label {{ color: #718093; margin-top: 5px; }}
  .card.awaiting .num {{ color: #fbc531; }}
  .card.in-progress .num {{ color: #0097e6; }}
  .card.done .num {{ color: #44bd32; }}
  .card.total .num {{ color: #2f3640; }}
  .section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
  .section h2 {{ margin-top: 0; border-bottom: 2px solid #f5f6fa; padding-bottom: 10px; }}
  .req {{ border-left: 4px solid #dcdde1; padding: 15px; margin-bottom: 15px; background: #fafbfc; border-radius: 0 4px 4px 0; }}
  .req.awaiting {{ border-left-color: #fbc531; }}
  .req.in-progress {{ border-left-color: #0097e6; }}
  .req.done {{ border-left-color: #44bd32; }}
  .req.cancelled {{ border-left-color: #c23616; opacity: 0.6; }}
  .req-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
  .req-title {{ font-weight: bold; font-size: 16px; }}
  .req-stage {{ padding: 3px 12px; border-radius: 12px; background: #dcdde1; font-size: 12px; }}
  .req-stage.awaiting {{ background: #fbc531; color: white; }}
  .req-stage.in-progress {{ background: #0097e6; color: white; }}
  .req-stage.done {{ background: #44bd32; color: white; }}
  .progress-bar {{ display: flex; gap: 4px; margin-top: 10px; }}
  .progress-step {{ flex: 1; height: 30px; background: #ecf0f1; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #7f8c8d; }}
  .progress-step.done {{ background: #44bd32; color: white; }}
  .progress-step.current {{ background: #0097e6; color: white; font-weight: bold; }}
  .progress-step.current.awaiting {{ background: #fbc531; }}
  .progress-step.current.fixing {{ background: #e74c3c; }}
  .summary-text {{ color: #57606f; font-size: 14px; margin-top: 8px; }}
  .req-links {{ margin-top: 10px; font-size: 13px; }}
  .req-links a {{ color: #0097e6; margin-right: 15px; text-decoration: none; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #f5f6fa; }}
  th {{ color: #718093; font-weight: normal; }}
</style>
</head>
<body>

<h1>📋 Project Status Board</h1>
<div class="meta">Last updated: {now}</div>

<div class="summary">
  <div class="card total"><div class="num">{total}</div><div class="label">Total</div></div>
  <div class="card awaiting"><div class="num">{awaiting_count}</div><div class="label">Awaiting</div></div>
  <div class="card in-progress"><div class="num">{in_progress_count}</div><div class="label">In progress</div></div>
  <div class="card done"><div class="num">{done_count}</div><div class="label">Done</div></div>
</div>
"""

    # Awaiting your approval
    awaiting = [(rid, g) for rid, g in groups.items() if get_canonical_stage(g).startswith("awaiting-")]
    if awaiting:
        html += '<div class="section"><h2>🛑 Awaiting your approval</h2><table>'
        html += '<tr><th>ID</th><th>Title</th><th>Waiting for</th><th>Waiting since</th></tr>'
        for rid, g in awaiting:
            prd = g.get("prd", {})
            stage = get_canonical_stage(g)
            _, label = STAGE_LABEL.get(stage, ("⚪", stage))
            html += f'<tr><td><strong>PRD-{rid}</strong></td><td>{prd.get("title", "")}</td><td>{label}</td><td>{prd.get("updated", "")}</td></tr>'
        html += '</table></div>'

    # Details
    html += '<div class="section"><h2>📋 Details</h2>'

    sorted_reqs = sorted(
        groups.items(),
        key=lambda x: (STAGE_ORDER.get(get_canonical_stage(x[1]), 999), x[0])
    )

    for rid, g in sorted_reqs:
        prd = g.get("prd", {})
        stage = get_canonical_stage(g)
        icon, label = STAGE_LABEL.get(stage, ("⚪", stage))

        if stage.startswith("awaiting-"):
            css_class = "awaiting"
        elif stage in ("deployed",):
            css_class = "done"
        elif stage == "cancelled":
            css_class = "cancelled"
        else:
            css_class = "in-progress"

        progress = get_stage_progress(g)
        progress_html = ""
        for ico, lbl in progress:
            if ico == "✅":
                cls = "done"
            elif ico in ["🟦", "🟪", "🟧", "🟨"]:
                cls = "current"
            elif ico == "🟡":
                cls = "current awaiting"
            elif ico == "🔴":
                cls = "current fixing"
            else:
                cls = ""
            progress_html += f'<div class="progress-step {cls}">{lbl}</div>'

        html += f"""
<div class="req {css_class}">
  <div class="req-header">
    <div class="req-title">PRD-{rid}: {prd.get("title", "")}</div>
    <div class="req-stage {css_class}">{icon} {label}</div>
  </div>
  <div class="summary-text">{prd.get("summary", "")}</div>
  <div class="progress-bar">{progress_html}</div>
  <div class="req-links">
"""
        if "prd" in g:
            html += f'<a href="{g["prd"]["path"]}">📄 PRD</a>'
        if "spec" in g:
            html += f'<a href="{g["spec"]["path"]}">⚙️ SPEC</a>'
        if "test-plan" in g:
            html += f'<a href="{g["test-plan"]["path"]}">🧪 TEST-PLAN</a>'
        html += '</div></div>'

    html += '</div>'

    # Backlog summary
    backlog = load_backlog()
    open_items = [b for b in backlog if b["status"] == "open"]
    if open_items:
        p0 = [b for b in open_items if b["priority"] == "P0"]
        p1 = [b for b in open_items if b["priority"] == "P1"]
        p2 = [b for b in open_items if b["priority"] == "P2"]
        html += '<div class="section"><h2>📥 Backlog</h2>'
        html += f'<p style="color:#718093">{len(open_items)} open — <strong>P0: {len(p0)}</strong> &nbsp; P1: {len(p1)} &nbsp; P2: {len(p2)}</p>'
        if p0 or p1:
            html += '<table><tr><th>ID</th><th>Title</th><th>Priority</th><th>Source</th></tr>'
            for b in p0 + p1:
                color = "#e74c3c" if b["priority"] == "P0" else "#f39c12"
                html += f'<tr><td><strong>{b["id"]}</strong></td><td>{b["title"]}</td><td style="color:{color};font-weight:bold">{b["priority"]}</td><td>{b["source"]}</td></tr>'
            html += '</table>'
        html += '</div>'

    html += '</body></html>'
    return html


def main():
    docs = load_all_docs()
    groups = group_by_requirement(docs)

    if not groups:
        print("⚠️  No requirement documents found (PRD-XXX.md)")
        return

    # Generate markdown
    md_content = render_markdown(groups)
    with open(STATUS_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"✅ STATUS.md generated ({len(groups)} requirements)")

    # Generate HTML
    html_content = render_html(groups)
    with open(STATUS_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ status.html generated")


if __name__ == "__main__":
    main()
