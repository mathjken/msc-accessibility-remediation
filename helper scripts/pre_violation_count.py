import os
import json
import csv
import re

# === Root directory ===
root_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data"
output_csv = os.path.join(root_path, "wcag_critical_violations_allfiles.csv")

# === WCAG mappings (strict rules for SC 1.3.1 and 4.1.2) ===
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

# === Sanitize check for file names (avoid Windows-invalid chars)
valid_filename_pattern = re.compile(r'^[\w\-\. ()\[\]{}@!&\',=]+$')

# === Normalize HTML file references ===
html_lookup = {}
for subdir, _, files in os.walk(root_path):
    for f in files:
        if f.endswith(".html"):
            key = os.path.splitext(f)[0].lower().replace("www.", "").replace("-", "").replace("_", "")
            html_lookup[key] = os.path.join(subdir, f)

# === Collect results ===
results = []

for subdir, _, files in os.walk(root_path):
    for file in files:
        if not file.endswith(".jsonld"):
            continue

        # ⛔ Skip files with invalid/special characters
        if not valid_filename_pattern.match(file):
            print(f"❌ Skipped invalid filename: {file}")
            continue

        file_path = os.path.join(subdir, file)
        base_key = os.path.splitext(file)[0].lower().replace("www.", "").replace("-", "").replace("_", "")
        html_path = html_lookup.get(base_key, "")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Skipped {file}: {e}")
            continue

        # If wrapped inside "accessibility", unwrap
        if isinstance(data, dict) and "accessibility" in data and isinstance(data["accessibility"], dict):
            data = data["accessibility"]

        violations = data.get("violations", [])
        if not isinstance(violations, list):
            continue

        wcag_131 = 0
        wcag_412 = 0

        for violation in violations:
            if not isinstance(violation, dict):
                continue

            rule_id = violation.get("id", "").lower()
            impact = violation.get("impact", "")
            tags = violation.get("tags", [])
            if not isinstance(impact, str) or impact.lower() != "critical":
                continue

            nodes = violation.get("nodes", [])
            for node in nodes:
                html = node.get("html", "")
                target = node.get("target", [""])[0] if isinstance(node.get("target", []), list) else node.get("target", "")

                wcag_match = ""
                for sc, sc_data in WCAG_RULES.items():
                    if rule_id in sc_data["rules"]:
                        wcag_match = sc
                        if sc == "1.3.1":
                            wcag_131 += 1
                        elif sc == "4.1.2":
                            wcag_412 += 1

                        results.append({
                            "file": file,
                            "rule_id": rule_id,
                            "impact": impact,
                            "wcag_1.3.1": wcag_131,
                            "wcag_4.1.2": wcag_412,
                            "html": html,
                            "target": target,
                            "violation_count": len(nodes),
                            "tags": ", ".join(tags),
                            "html_file_path": html_path
                        })

# === Write to CSV ===
fieldnames = [
    "file", "rule_id", "impact", "wcag_1.3.1", "wcag_4.1.2",
    "html", "target", "violation_count", "tags", "html_file_path"
]

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("✅ WCAG critical violations summary written to:")
print(f"📄 {output_csv}")
