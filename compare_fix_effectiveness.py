import json
import csv
import os

# === File Paths ===
original_path = "clustered_violations_mapped.json"
cot_path = "axe_scan_reports/axe_result_cot_0.json"
rag_path = "axe_scan_reports/axe_result_rag_0.json"
output_csv = "detailed_fix_comparison_per_violation.csv"

# === Helper: Load failing rule_ids from scan result ===
def extract_failures(scan_path):
    if not os.path.exists(scan_path):
        print(f"⚠️ Missing file: {scan_path}")
        return set()
    with open(scan_path, "r", encoding="utf-8") as f:
        scan = json.load(f)
    failing = set()
    for section in ["violations", "incomplete"]:
        for rule in scan.get(section, []):
            if rule.get("nodes"):
                failing.add(rule["id"].lower())
    return failing

# === Load original violations ===
with open(original_path, "r", encoding="utf-8") as f:
    original_data = json.load(f)

original_critical_rules = {v["rule_id"].lower() for v in original_data if v.get("impact") == "critical"}

# === Load CoT and RAG failures ===
cot_failures = extract_failures(cot_path)
rag_failures = extract_failures(rag_path)

# === Generate detailed rows ===
detailed_rows = []

# Track all rule IDs that were part of the original data
original_rule_ids = {v["rule_id"].lower() for v in original_data}

for entry in original_data:
    rule_id = entry.get("rule_id", "").lower()
    for method, failures in [("CoT", cot_failures), ("RAG", rag_failures)]:
        is_fixed = rule_id not in failures
        is_original = rule_id in original_critical_rules
        is_new = not is_original and rule_id in failures

        if is_new:
            pass_status = "⚠️ New Violation"
        elif is_original:
            pass_status = "✅ Pass" if is_fixed else "❌ Fail"
        else:
            pass_status = "⚠️ Not originally critical"

        row = {
            "method": method,
            "rule_id": rule_id,
            "impact": entry.get("impact", ""),
            "file": entry.get("file", ""),
            "html": entry.get("html", ""),
            "wcag_guideline": entry.get("wcag_guideline", ""),
            "wcag_description": entry.get("wcag_description", ""),
            "wcag_techniques": entry.get("wcag_techniques", ""),
            "fix_status": "✅ Fixed" if is_fixed else "Not Fixed",
            "is_new_violation": "Yes" if is_new else "No",
            "pass_per_row": pass_status
        }
        detailed_rows.append(row)

# === Save to CSV ===
fieldnames = list(detailed_rows[0].keys())
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(detailed_rows)

print(f"✅ Detailed fix comparison (including new violations) saved to: {output_csv}")
