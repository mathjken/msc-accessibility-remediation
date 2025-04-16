import os
import json
import csv

# Root path to search through
root_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data"

# Output paths
report_csv = os.path.join(root_path, "violation_integrity_report.csv")
summary_json = os.path.join(root_path, "violation_summary.json")
filtered_output = os.path.join(root_path, "filtered_violations_131_412.json")
url_csv_output = os.path.join(root_path, "violations_urls.csv")

# Storage
target_criteria = {
    "1.3.1": [],
    "4.1.2": []
}
integrity_report = []
parsed_count = 0
skipped_count = 0

# --- Helper: Add entry if match found ---
def check_and_append(tags, rule_id, entry):
    tag_string = " ".join(tags).lower()
    is_aria = rule_id.startswith("aria-")

    if "wcag131" in tag_string or "1.3.1" in tag_string or (is_aria and "131" in tag_string):
        target_criteria["1.3.1"].append(entry)
    if "wcag412" in tag_string or "4.1.2" in tag_string or (is_aria and "412" in tag_string):
        target_criteria["4.1.2"].append(entry)

# --- Scan and parse ---
for subdir, _, files in os.walk(root_path):
    for filename in files:
        if filename.endswith((".json", ".jsonld")):
            file_path = os.path.join(subdir, filename)
            print(f"🔍 Processing: {filename}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError as e:
                        skipped_count += 1
                        integrity_report.append({
                            "file": filename,
                            "status": "skipped",
                            "path": file_path,
                            "error": f"JSONDecodeError: {str(e)}"
                        })
                        continue

                parsed_count += 1

                if isinstance(data, dict) and "violations" in data:
                    for violation in data["violations"]:
                        tags = violation.get("tags", [])
                        nodes = violation.get("nodes", [])
                        html = nodes[0].get("html", "") if nodes else ""
                        target = nodes[0].get("target", "") if nodes else ""
                        impact = violation.get("impact", "")
                        rule_id = violation.get("id", "")

                        entry = {
                            "file": filename,
                            "file_path": file_path,
                            "rule_id": rule_id,
                            "impact": impact,
                            "html": html,
                            "target": target
                        }

                        check_and_append(tags, rule_id, entry)

                integrity_report.append({
                    "file": filename,
                    "status": "parsed",
                    "path": file_path,
                    "error": ""
                })

            except Exception as e:
                skipped_count += 1
                integrity_report.append({
                    "file": filename,
                    "status": "skipped",
                    "path": file_path,
                    "error": str(e)
                })

# --- Write CSV Report ---
with open(report_csv, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["file", "status", "path", "error"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in integrity_report:
        writer.writerow(row)

# --- Write Violation Summary ---
summary_counts = {
    "parsed_files": parsed_count,
    "skipped_files": skipped_count,
    "total_1.3.1_violations": len(target_criteria["1.3.1"]),
    "total_4.1.2_violations": len(target_criteria["4.1.2"])
}
with open(summary_json, "w", encoding="utf-8") as f:
    json.dump(summary_counts, f, indent=2)

# --- Write Filtered Violations ---
with open(filtered_output, "w", encoding="utf-8") as f:
    json.dump(target_criteria, f, indent=2)

# --- Write CSV of Violations ---
with open(url_csv_output, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["file", "rule_id", "impact", "WCAG_SC", "html", "target"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for sc, violations in target_criteria.items():
        for v in violations:
            writer.writerow({
                "file": v["file"],
                "rule_id": v["rule_id"],
                "impact": v["impact"],
                "WCAG_SC": sc,
                "html": v["html"],
                "target": v["target"]
            })

# --- Final Message ---
print("✅ DONE!")
print(f"Parsed: {parsed_count} | Skipped: {skipped_count}")
print(f"1.3.1 Violations: {len(target_criteria['1.3.1'])}")
print(f"4.1.2 Violations: {len(target_criteria['4.1.2'])}")
print("📁 Files saved:")
print(f"- {report_csv}")
print(f"- {summary_json}")
print(f"- {filtered_output}")
print(f"- {url_csv_output}")