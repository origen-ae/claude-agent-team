#!/usr/bin/env python3
"""Scan docs/ to generate a global index"""
import sys
import yaml
import frontmatter
from pathlib import Path
from datetime import datetime

# Make emoji/UTF-8 output safe on consoles with a non-UTF-8 default encoding
# (e.g. Windows GBK). No-op if reconfigure is unavailable or fails.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).parent.parent
DOCS_ROOT = ROOT / "docs"
INDEX_PATH = DOCS_ROOT / "index.yaml"

REQUIRED_FIELDS = ["id", "title", "type", "stage", "owner", "updated"]


def scan():
    documents = []
    errors = []
    seen_ids = {}

    for md_file in DOCS_ROOT.rglob("*.md"):
        if md_file.name in ("README.md", "index.yaml", "backlog.md"):
            continue
        if "_templates" in md_file.parts:
            continue

        try:
            post = frontmatter.load(md_file)
            fm = post.metadata
            missing = [f for f in REQUIRED_FIELDS if f not in fm]
            if missing:
                errors.append(f"{md_file.relative_to(ROOT)}: missing fields {missing}")
                continue

            doc_id = fm["id"]
            if doc_id in seen_ids:
                errors.append(f"{md_file.relative_to(ROOT)}: duplicate ID {doc_id}")
                continue
            seen_ids[doc_id] = str(md_file.relative_to(ROOT))

            entry = {
                "id": doc_id,
                "title": fm["title"],
                "type": fm["type"],
                "stage": fm["stage"],
                "owner": fm["owner"],
                "updated": str(fm["updated"]),
                "summary": fm.get("summary", "").strip(),
                "path": str(md_file.relative_to(ROOT)),
            }
            for opt in ["tags", "related", "module", "priority", "created"]:
                if opt in fm:
                    entry[opt] = fm[opt]

            documents.append(entry)

        except Exception as e:
            errors.append(f"{md_file.relative_to(ROOT)}: parse failed {e}")

    return documents, errors


def main():
    documents, errors = scan()

    by_type = {}
    by_stage = {}
    for doc in documents:
        by_type[doc["type"]] = by_type.get(doc["type"], 0) + 1
        by_stage[doc["stage"]] = by_stage.get(doc["stage"], 0) + 1

    output = {
        "generated-at": datetime.now().isoformat(),
        "total": len(documents),
        "by-type": by_type,
        "by-stage": by_stage,
        "documents": sorted(documents, key=lambda d: d["id"]),
    }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(output, f, allow_unicode=True, sort_keys=False)

    print(f"✅ Index: {INDEX_PATH}")
    print(f"   Total: {len(documents)} | by type: {by_type}")

    if errors:
        print(f"\n⚠️  {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
