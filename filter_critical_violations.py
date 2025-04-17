import os
import json
import csv

# Root directory to scan
root_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data"

# Output file paths
report_csv = os.path.join(root_path, "violation_integrity_critical_report.csv")
summary_json = os.path.join(root_path, "violation_summary_critical.json")
filtered_output = os.path.join(root_path, "filtered_violations_131_412_critical.json")
url_csv_output = os.path.join(root_path, "violations_urls_critical.csv")

# Results containers
target_criteria = {"1.3.1": [], "4.1.2": []}
integrity_report = []
parsed_count = 0
skipped_count = 0

# WCAG mapping for accuracy
WCAG_RULES = {
    "1.3.1": {
        "tags": ["wcag131", "wcag2a", "wcag20:1.3.1"],
        "rule_ids": [
            "aria-required-children", "aria-required-parent", "definition-list",
            "dlitem", "landmark-banner-is-top-level", "landmark-main-is-top-level",
            "landmark-contentinfo-is-top-level"
        ]
    },
    "4.1.2": {
        "tags": ["wcag412", "wcag2a", "wcag20:4.1.2"],
        "rule_ids": [
            "aria-command-name", "aria-input-field-name", "aria-toggle-field-name",
            "aria-tooltip-name", "aria-roledescription", "select-name",
            "aria-treeitem-name"
        ]
    }
}

# Matching function
def is_match(taglist, rule_id, target):
    tag_string = " ".join(taglist).lower()
    rule_id = rule_id.lower()
    rule_ids = WCAG_RULES[target]["rule_ids"]
    tags = WCAG_RULES[target]["tags"]

    matched_by_tag = any(t in tag_string for t in tags)
    matched_by_rule_id = rule_id in rule_ids
    return matched_by_tag or matched_by_rule_id, "tag" if matched_by_tag else "rule_id" if matched_by_rule_id else "none"

# Scan files
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

                accessibility_data = data.get("accessibility", {})
                for section in ["violations", "incomplete", "inapplicable"]:
                    for violation in accessibility_data.get(section, []):
                        impact = violation.get("impact", "")
                        if impact != "critical":
                            continue  # Filter only critical

                        tags = [t.lower() for t in violation.get("tags", [])]
                        rule_id = violation.get("id", "").lower()
                        nodes = violation.get("nodes", [])
                        html = nodes[0].get("html", "") if nodes else ""
                        target = nodes[0].get("target", "") if nodes else ""

                        for sc in target_criteria:
                            matched, source = is_match(tags, rule_id, sc)
                            if matched:
                                entry = {
                                    "file": filename,
                                    "file_path": file_path,
                                    "rule_id": rule_id,
                                    "impact": impact,
                                    "html": html,
                                    "target": target,
                                    "tags": tags,
                                    "nodes": nodes,
                                    "matched_by": source
                                }
                                target_criteria[sc].append(entry)

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

# Save integrity report
with open(report_csv, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["file", "status", "path", "error"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in integrity_report:
        writer.writerow(row)

# Save summary
summary_counts = {
    "parsed_files": parsed_count,
    "skipped_files": skipped_count,
    "total_1.3.1_violations": len(target_criteria["1.3.1"]),
    "total_4.1.2_violations": len(target_criteria["4.1.2"])
}
with open(summary_json, "w", encoding="utf-8") as f:
    json.dump(summary_counts, f, indent=2)

# Save filtered critical violations JSON
with open(filtered_output, "w", encoding="utf-8") as f:
    json.dump(target_criteria, f, indent=2)

# Save CSV (optional)
with open(url_csv_output, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = [
        "file", "rule_id", "impact", "WCAG_SC", "html", "target",
        "tags", "nodes", "matched_by"
    ]
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
                "target": v["target"],
                "tags": json.dumps(v["tags"]),
                "nodes": json.dumps(v["nodes"]),
                "matched_by": v.get("matched_by", "N/A")
            })

# Done
print("\n✅ DONE!")
print(f"Parsed: {parsed_count} | Skipped: {skipped_count}")
print(f"1.3.1 Critical Violations: {len(target_criteria['1.3.1'])}")
print(f"4.1.2 Critical Violations: {len(target_criteria['4.1.2'])}")
print("\n📁 Files saved:")
print(f"- {report_csv}")
print(f"- {summary_json}")
print(f"- {filtered_output}")
print(f"- {url_csv_output}")