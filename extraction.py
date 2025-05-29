import os
import json
import csv

# === Root directory ===
root_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data"

# === Output paths ===
report_csv = os.path.join(root_path, "violation_integrity_critical_report.csv")
summary_json = os.path.join(root_path, "violation_summary_critical.json")
filtered_output = os.path.join(root_path, "filtered_violations_131_412_critical.json")
url_csv_output = os.path.join(root_path, "violations_urls_critical.csv")
violation_counts_csv = os.path.join(root_path, "violation_counts_per_file.csv")  # 🔹 NEW

# === WCAG mappings (strict rules for critical re-filter) ===
WCAG_RULES = {
    "1.3.1": {
        "rules": [
            "aria-required-parent", "aria-required-children", "landmark-one-main",
            "region", "form-field-multiple-labels"
        ],
        "description": "Information and Relationships"
    },
    "4.1.2": {
        "rules": [
            "aria-label", "aria-labelledby", "button-name", "aria-valid-attr",
            "aria-valid-attr-value", "aria-allowed-attr", "aria-hidden-focus"
        ],
        "description": "Name, Role, Value"
    }
}

# === Results containers ===
refiltered = {"1.3.1": [], "4.1.2": []}
integrity_report = []
violation_counts = []
parsed_count = 0
skipped_count = 0

# === Normalize HTML file references ===
html_lookup = {}
for subdir, _, files in os.walk(root_path):
    for f in files:
        if f.endswith(".html"):
            key = os.path.splitext(f)[0].lower().replace("www.", "").replace("-", "").replace("_", "")
            html_lookup[key] = os.path.join(subdir, f)

# === Scan & filter JSON ===
for subdir, _, files in os.walk(root_path):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(subdir, filename)
            base_key = os.path.splitext(filename)[0].lower().replace("www.", "").replace("-", "").replace("_", "")
            html_path = html_lookup.get(base_key, "")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                skipped_count += 1
                continue

            parsed_count += 1
            accessibility_data = data.get("accessibility", {})
            critical_131 = 0
            critical_412 = 0

            for section in ["violations", "incomplete", "inapplicable"]:
                for violation in accessibility_data.get(section, []):
                    rule_id = violation.get("id", "").lower()
                    impact = violation.get("impact", "").lower()
                    nodes = violation.get("nodes", [])
                    html = nodes[0].get("html", "") if nodes else ""
                    target = nodes[0].get("target", "") if nodes else ""

                    if impact != "critical":
                        continue

                    for sc, sc_data in WCAG_RULES.items():
                        if rule_id in sc_data["rules"]:
                            if sc == "1.3.1":
                                critical_131 += 1
                            elif sc == "4.1.2":
                                critical_412 += 1

                            entry = {
                                "file": filename,
                                "rule_id": rule_id,
                                "impact": impact,
                                "WCAG_SC": sc,
                                "html": html,
                                "target": target,
                                "html_file_path": html_path
                            }
                            refiltered[sc].append(entry)
                            integrity_report.append({
                                "file": filename,
                                "status": "retained",
                                "rule_id": rule_id,
                                "impact": impact,
                                "SC": sc,
                                "html_file_path": html_path
                            })

            # 🔹 Save per-file violation count
            violation_counts.append({
                "file": filename,
                "critical_1.3.1": critical_131,
                "critical_4.1.2": critical_412,
                "total_critical": critical_131 + critical_412
            })

# === Save CSV violation counts ===
with open(violation_counts_csv, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["file", "critical_1.3.1", "critical_4.1.2", "total_critical"])
    writer.writeheader()
    writer.writerows(violation_counts)

print("✅ Violation count summary saved to:", violation_counts_csv)
