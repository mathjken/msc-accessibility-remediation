import json
import csv
import os
from collections import Counter

# Load from previously filtered file (from the critical filtering script)
#input_file = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data\filtered_violations_131_412_critical.json"
input_file = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data\filtered_violations_131_412_critical.json"

# Output paths
output_csv = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\data\refiltered_violations_131_412.csv"
output_summary = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\data\refiltered_summary.json"
output_json = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\data\refiltered_violations_131_412.json"

# Target WCAG rule IDs for re-filtering
WCAG_RULES = {
    "1.3.1": [
        "aria-required-parent",
        "aria-required-children",
        "landmark-one-main",
        "region",
        "form-field-multiple-labels"
    ],
    "4.1.2": [
        "aria-label",
        "aria-labelledby",
        "button-name",
        "aria-valid-attr",
        "aria-valid-attr-value",
        "aria-allowed-attr",
        "aria-hidden-focus"
    ]
}

# Load the previously filtered JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Prepare new filtered results
refiltered = {"1.3.1": [], "4.1.2": []}

for sc, rule_ids in WCAG_RULES.items():
    for item in data.get(sc, []):
        if item["rule_id"] in rule_ids:
            refiltered[sc].append(item)

# Save the new filtered CSV
with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = [
        "file", "rule_id", "impact", "WCAG_SC", "html", "target",
        "tags", "nodes", "matched_by"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for sc, violations in refiltered.items():
        for v in violations:
            writer.writerow({
                "file": v.get("file"),
                "rule_id": v.get("rule_id"),
                "impact": v.get("impact"),
                "WCAG_SC": sc,
                "html": v.get("html"),
                "target": v.get("target"),
                "tags": json.dumps(v.get("tags")),
                "nodes": json.dumps(v.get("nodes")),
                "matched_by": v.get("matched_by", "N/A")
            })

# Save JSON summary
summary = {
    "total_1.3.1": len(refiltered["1.3.1"]),
    "total_4.1.2": len(refiltered["4.1.2"])
}
with open(output_summary, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

# Save refiltered JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(refiltered, f, indent=2)

# ✅ Display summary
print("\n✅ Refined filter complete!")
print(f"SC 1.3.1: {summary['total_1.3.1']} violations")
print(f"SC 4.1.2: {summary['total_4.1.2']} violations")

# 🔢 Rule frequency breakdown
print("\n🔍 Rule ID Frequencies:")

rule_counts = {
    sc: Counter([item["rule_id"] for item in refiltered[sc]])
    for sc in refiltered
}

for sc, counts in rule_counts.items():
    print(f"\n{sc} Breakdown:")
    for rule, count in counts.items():
        print(f"  - {rule}: {count}")
