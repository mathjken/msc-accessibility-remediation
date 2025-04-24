import json
import csv
import os

# Input files
clustered_json_path = "clustered_violations_mapped.json"
scan_results_dir = "axe_scan_reports"
output_csv_path = "violation_fix_comparison_dual.csv"

# Collect failing rules from each Axe scan (RAG and CoT)
def extract_failing_rules(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    failing_rules = set()
    for section in ["violations", "incomplete", "inapplicable"]:
        for rule in data.get(section, []):
            if "id" in rule and rule.get("nodes"):
                failing_rules.add(rule["id"].lower())
    return failing_rules

# Load all scan result files
scan_files = {
    "cot": os.path.join(scan_results_dir, "axe_result_cot_0.json"),  # adjust index if needed
    "rag": os.path.join(scan_results_dir, "axe_result_rag_0.json")   # adjust index if needed
}

# Build lookup per fix type
failing_rules_by_type = {}
for fix_type, path in scan_files.items():
    if os.path.exists(path):
        failing_rules_by_type[fix_type] = extract_failing_rules(path)
    else:
        failing_rules_by_type[fix_type] = set()
        print(f"⚠️ Missing scan file: {path}")

# Load clustered violations
with open(clustered_json_path, "r", encoding="utf-8") as f:
    clustered_violations = json.load(f)

# Annotate each entry with fix status per type
results = []
for entry in clustered_violations:
    rule_id = entry.get("rule_id", "").lower()

    for fix_type in ["cot", "rag"]:
        result_entry = entry.copy()
        result_entry["source_file"] = fix_type
        result_entry["fix_status"] = "Not Fixed" if rule_id in failing_rules_by_type[fix_type] else "✅ Fixed"

        # Remove clustering columns if present
        result_entry.pop("kmeans_cluster", None)
        result_entry.pop("dbscan_cluster", None)

        results.append(result_entry)

# Write annotated results to CSV
fieldnames = list(results[0].keys())
with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Dual comparison complete. Results saved to: {output_csv_path}")
