import json
import csv

# File paths
input_json_path = "results_cot_rag_generated.json"
output_csv_path = "manual_comparison_old_new.csv"

# Load clustered violations
with open(input_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Generate CSV rows
rows = []
for entry in data:
    row_id = entry.get("id", "")
    rule_id = entry.get("rule_id", "")
    original_html = entry.get("html", "").strip()
    cot_fix = entry.get("cot_response", "").strip()
    rag_fix = entry.get("rag_response", "").strip()

    row = {
        "id": row_id,
        "rule_id": rule_id,
        "original_html": original_html,
        "cot_fixed_html": cot_fix,
        "rag_fixed_html": rag_fix,
        "fix_completeness": "",
        "fix_correctness": "",
        "wcag_alignment": "",
        "comments": ""
    }
    rows.append(row)

# Write to CSV
fieldnames = list(rows[0].keys())
with open(output_csv_path, "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Manual comparison CSV saved to: {output_csv_path}")
