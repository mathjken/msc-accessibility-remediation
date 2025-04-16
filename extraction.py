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

# --- Scan and parse ---
for subdir, _, files in os.walk(root_path):
    for filename in files:
        if filename.endswith((".json", ".jsonld")):
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
                        continue  # Skip to next file

                parsed_count += 1

                # Sections to check
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

                        # Match for SC 1.3.1
                        if (
                            "wcag131" in tags or
                            "wcag1.3.1" in tags or
                            "wcag20:1.3.1" in tags or
                            "1.3.1" in tags or
                            ("aria-" in rule_id and "131" in rule_id)
                        ):
                            print("✅ Found 1.3.1 match in:", filename, "| Rule:", rule_id)
                            target_criteria["1.3.1"].append(entry)

                        # Match for SC 4.1.2
                        if (
                            "wcag412" in tags or
                            "wcag4.1.2" in tags or
                            "wcag20:4.1.2" in tags or
                            "4.1.2" in tags or
                            ("aria-" in rule_id and "412" in rule_id)
                        ):
                            print("✅ Found 4.1.2 match in:", filename, "| Rule:", rule_id)
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
print("\n✅ DONE!")
print(f"Parsed: {parsed_count} | Skipped: {skipped_count}")
print(f"1.3.1 Violations: {len(target_criteria['1.3.1'])}")
print(f"4.1.2 Violations: {len(target_criteria['4.1.2'])}")
print("📁 Files saved:")
print(f"- {report_csv}")
print(f"- {summary_json}")
print(f"- {filtered_output}")
print(f"- {url_csv_output}")
