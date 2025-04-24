import json
import csv
import os

# Input path
input_file = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\clustered_violations.json"

# Output paths
base_path = os.path.dirname(input_file)
json_output = os.path.join(base_path, "clustered_violations_mapped.json")
csv_output = os.path.join(base_path, "clustered_violations_mapped.csv")

# Axe-Core rule IDs mapped to their WCAG techniques
wcag_mapping = {
    # SC 1.3.1 – Info and Relationships
    "aria-required-parent": {
        "wcag_sc": "1.3.1",
        "wcag_description": "Info and Relationships",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html",
        "techniques": [
            {"id": "ARIA12", "desc": "Using role=heading to identify headings"},
            {"id": "ARIA17", "desc": "Using group role to associate related form controls"}
        ]
    },
    "aria-required-children": {
        "wcag_sc": "1.3.1",
        "wcag_description": "Info and Relationships",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html",
        "techniques": [
            {"id": "ARIA11", "desc": "Using ARIA landmarks to identify regions"},
            {"id": "ARIA12", "desc": "Using role=heading to identify headings"},
            {"id": "ARIA17", "desc": "Using group role to associate related form controls"},
            {"id": "ARIA20", "desc": "Using the region role to identify a region of the page"},
            {"id": "ARIA13", "desc": "Using aria-labelledby to name regions and widgets"}
        ]
    },
    "landmark-one-main": {
        "wcag_sc": "1.3.1",
        "wcag_description": "Info and Relationships",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html",
        "techniques": [
            {"id": "ARIA11", "desc": "Using ARIA landmarks to identify regions"}
        ]
    },
    "region": {
        "wcag_sc": "1.3.1",
        "wcag_description": "Info and Relationships",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html",
        "techniques": [
            {"id": "ARIA20", "desc": "Using the region role to identify a region of the page"}
        ]
    },
    "form-field-multiple-labels": {
        "wcag_sc": "1.3.1",
        "wcag_description": "Info and Relationships",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html",
        "techniques": [
            {"id": "H44", "desc": "Using label elements to associate text labels with form controls"}
        ]
    },

    # SC 4.1.2 – Name, Role, Value
    "aria-label": {
        "wcag_sc": "4.1.2",
        "wcag_description": "Name, Role, Value",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html",
        "techniques": [
            {"id": "ARIA14", "desc": "Using aria-label to provide an invisible label"},
            {"id": "ARIA16", "desc": "Using aria-labelledby to name controls"},
            {"id": "G108", "desc": "Using markup to associate a label with a form control"}
        ]
    },
    "aria-labelledby": {
        "wcag_sc": "4.1.2",
        "wcag_description": "Name, Role, Value",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html",
        "techniques": [
            {"id": "ARIA16", "desc": "Using aria-labelledby to name controls"},
            {"id": "ARIA14", "desc": "Using aria-label to provide an invisible label"}
        ]
    },
    "button-name": {
        "wcag_sc": "4.1.2",
        "wcag_description": "Name, Role, Value",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html",
        "techniques": [
            {"id": "G108", "desc": "Using markup to associate a label with a control"},
            {"id": "ARIA14", "desc": "Using aria-label to provide an invisible label"}
        ]
    },
    "aria-valid-attr": {
        "wcag_sc": "4.1.2",
        "wcag_description": "Name, Role, Value",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html",
        "techniques": [
            {"id": "ARIA5", "desc": "Using WAI-ARIA state and property attributes correctly"}
        ]
    },
    "aria-valid-attr-value": {
        "wcag_sc": "4.1.2",
        "wcag_description": "Name, Role, Value",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html",
        "techniques": [
            {"id": "ARIA5", "desc": "Using WAI-ARIA state and property attributes correctly"}
        ]
    },
    "aria-allowed-attr": {
        "wcag_sc": "4.1.2",
        "wcag_description": "Name, Role, Value",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html",
        "techniques": [
            {"id": "ARIA5", "desc": "Using WAI-ARIA state and property attributes correctly"}
        ]
    },
    "aria-hidden-focus": {
        "wcag_sc": "4.1.2",
        "wcag_description": "Name, Role, Value",
        "wcag_url": "https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html",
        "techniques": [
            {"id": "ARIA5", "desc": "Using WAI-ARIA state and property attributes correctly"}
        ]
    }
}

# Load original data
with open(input_file, "r", encoding="utf-8") as f:
    violations = json.load(f)

# Filter and annotate
filtered = []
for v in violations:
    rule_id = v.get("rule_id")
    if rule_id in wcag_mapping:
        mapping = wcag_mapping[rule_id]
        v["wcag_guideline"] = mapping["wcag_sc"]
        v["wcag_description"] = mapping["wcag_description"]
        v["wcag_url"] = mapping["wcag_url"]
        v["wcag_techniques"] = mapping["techniques"]
        filtered.append(v)

# Save JSON output
with open(json_output, "w", encoding="utf-8") as f:
    json.dump(filtered, f, indent=2)

# Save CSV output
csv_fields = [
    "WCAG_SC", "rule_id", "impact", "html", "file", "impact_score",
    "kmeans_cluster", "dbscan_cluster",
    "wcag_guideline", "wcag_description", "wcag_url", "wcag_technique_ids"
]

with open(csv_output, mode='w', newline='', encoding='utf-8') as csv_out:
    #writer = csv.DictWriter(csv_out, fieldnames=csv_fields)
    writer = csv.DictWriter(
    csv_out,
    fieldnames=csv_fields,
    quoting=csv.QUOTE_ALL,          # <- Ensures all fields are wrapped in quotes
    quotechar='"',
    escapechar='\\'
)
    writer.writeheader()
    for v in filtered:
        technique_ids = ", ".join([t["id"] for t in v.get("wcag_techniques", [])])
        writer.writerow({
            "WCAG_SC": v.get("WCAG_SC"),
            "rule_id": v.get("rule_id"),
            "impact": v.get("impact"),
            "html": v.get("html"),
            "file": v.get("file"),
            "impact_score": v.get("impact_score"),
            "kmeans_cluster": v.get("kmeans_cluster"),
            "dbscan_cluster": v.get("dbscan_cluster"),
            "wcag_guideline": v.get("wcag_guideline"),
            "wcag_description": v.get("wcag_description"),
            "wcag_url": v.get("wcag_url"),
            "wcag_technique_ids": technique_ids
        })

print("✅ Mapping complete.")
print("📄 JSON: ", json_output)
print("📄 CSV: ", csv_output)
