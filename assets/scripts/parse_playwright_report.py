#!/usr/bin/env python3
"""
Parse Playwright test results (JSON report) and write the test metrics back into
the frontmatter of the corresponding TEST-PLAN documents.
This lets the STATUS dashboard show the latest test pass rate.

Usage:
  npx playwright test --reporter=json > playwright-report.json
  python scripts/parse_playwright_report.py playwright-report.json
"""
import sys
import json
import re
import frontmatter
from pathlib import Path
from collections import defaultdict

# Make emoji/UTF-8 output safe on consoles with a non-UTF-8 default encoding
# (e.g. Windows GBK). No-op if reconfigure is unavailable or fails.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).parent.parent


def parse_report(report_path):
    """Parse the Playwright JSON report, aggregating by PRD."""
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    # Playwright JSON structure: suites[].specs[].tests[]
    by_prd = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0, "failures": []})

    def walk_suite(suite, file_path=""):
        for spec in suite.get("specs", []):
            # Extract the PRD ID from the file path
            file_path_full = spec.get("file") or file_path
            m = re.search(r"PRD-(\d+)\.spec\.", file_path_full)
            if not m:
                continue
            prd_id = f"PRD-{m.group(1)}"

            for test in spec.get("tests", []):
                for result in test.get("results", []):
                    status = result.get("status")
                    if status == "passed":
                        by_prd[prd_id]["passed"] += 1
                    elif status == "failed":
                        by_prd[prd_id]["failed"] += 1
                        by_prd[prd_id]["failures"].append({
                            "title": spec.get("title"),
                            "error": (result.get("error", {}).get("message", "")[:200])
                        })
                    elif status == "skipped":
                        by_prd[prd_id]["skipped"] += 1

        for child in suite.get("suites", []):
            walk_suite(child, file_path)

    for suite in report.get("suites", []):
        walk_suite(suite)

    return dict(by_prd)


def update_test_plans(by_prd):
    """Update the frontmatter of the corresponding TEST-PLAN documents."""
    for prd_id, stats in by_prd.items():
        num = prd_id.replace("PRD-", "")
        test_plan_path = ROOT / "docs" / "test-plan" / f"TEST-PLAN-{num}.md"
        if not test_plan_path.exists():
            print(f"⚠️  Skipping {prd_id}: TEST-PLAN document does not exist")
            continue

        post = frontmatter.load(test_plan_path)
        post.metadata.setdefault("test-metrics", {})
        post.metadata["test-metrics"]["e2e"] = {
            "passed": stats["passed"],
            "failed": stats["failed"],
            "skipped": stats["skipped"],
            "pass-rate": (
                f"{stats['passed'] / (stats['passed'] + stats['failed']) * 100:.0f}%"
                if (stats['passed'] + stats['failed']) > 0
                else "N/A"
            ),
        }

        with open(test_plan_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

        print(f"✅ {prd_id}: passed {stats['passed']}, failed {stats['failed']}, skipped {stats['skipped']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_playwright_report.py <report-path>")
        sys.exit(1)

    report_path = sys.argv[1]
    by_prd = parse_report(report_path)

    if not by_prd:
        print("⚠️  No PRD-XXX test files were found in the report")
        return

    update_test_plans(by_prd)
    print(f"\nUpdated {len(by_prd)} TEST-PLAN(s) in total")


if __name__ == "__main__":
    main()
