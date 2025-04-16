import os
import json
import csv

# Root directory to scan
root_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data"

# Output file paths
report_csv = os.path.join(root_path, "violation_integrity_report.csv")
summary_json = os.path.join(root_path, "violation_summary.json")
filtered_output = os.path.join(root_path, "filtered_violations_131_412.json")
url_csv_output = os.path.join(root_path, "violations_urls.csv")

# Results containers
target_criteria = {"1.3.1": [], "4.1.2": []}
integrity_report = []
parsed_count = 0
skipped_count = 0

# Matching function
def is_match(taglist, rule_id, target):
    tag_string = " ".join(taglist).lower()
    rule_id = rule_id.lower()
    return (
        target in tag_string or
        f"wcag{target.replace('.', '')}" in tag_string or
        f"wcag20:{target}" in tag_string or
        ("aria-" in rule_id and target.replace('.', '') in rule_id)
    )

# Scan all files
for subdir, _, files in os.walk(root_path):
    for filename in files:
        if filename.endswith((".json", ".jsonld", ".jsonId")):

            file_path = os.path.join(subdir, filename)

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
                if parsed_count % 100 == 0:
                    print(f"Parsed {parsed_count} files...")

                for section in ["violations", "incomplete", "inapplicable"]:
                    for violation in data.get(section, []):
                        tags = [t.lower() for t in violation.get("tags", [])]
                        rule_id = violation.get("id", "").lower()
                        nodes = violation.get("nodes", [])
                        html = nodes[0].get("html", "") if nodes else ""
                        target = nodes[0].get("target", "") if nodes else ""
                        impact = violation.get("impact", "")

                        entry = {
                            "file": filename,
                            "file_path": file_path,
                            "rule_id": rule_id,
                            "impact": impact,
                            "html": html,
                            "target": target
                        }

                        if is_match(tags, rule_id, "1.3.1"):
                            target_criteria["1.3.1"].append(entry)
                        if is_match(tags, rule_id, "4.1.2"):
                            target_criteria["4.1.2"].append(entry)

                integrity_report.append({
                    "file": filename,
                    "status": "parsed",
                    "path": file_path
                })

            except Exception as e:
                skipped_count += 1
                integrity_report.append({
                    "file": filename,
                    "status": "skipped",
                    "path": file_path,
                    "error": str(e)
                })

# Save CSV integrity report
with open(report_csv, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["file", "status", "path", "error"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in integrity_report:
        writer.writerow(row)

# Save violation summary
summary_counts = {
    "parsed_files": parsed_count,
    "skipped_files": skipped_count,
    "total_1.3.1_violations": len(target_criteria["1.3.1"]),
    "total_4.1.2_violations": len(target_criteria["4.1.2"])
}
with open(summary_json, "w", encoding="utf-8") as f:
    json.dump(summary_counts, f, indent=2)

# Save filtered results
with open(filtered_output, "w", encoding="utf-8") as f:
    json.dump(target_criteria, f, indent=2)

# Save matching violations to CSV
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

# Done!
print("✅ DONE!")
print(f"Parsed: {parsed_count} | Skipped: {skipped_count}")
print(f"1.3.1 Violations: {len(target_criteria['1.3.1'])}")
print(f"4.1.2 Violations: {len(target_criteria['4.1.2'])}")
print("📁 Files saved:")
print(f"- {report_csv}")
print(f"- {summary_json}")
print(f"- {filtered_output}")
print(f"- {url_csv_output}")
