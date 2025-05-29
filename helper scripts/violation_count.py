import json
import pandas as pd
from collections import Counter

# === Load clustered JSON ===
with open("clustered_violations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# === Count how many violations per file ===
file_counts = Counter(entry.get("file", "") for entry in data)

records = []
for i, entry in enumerate(data):
    wcag_techniques = entry.get("wcag_techniques", [])
    if isinstance(wcag_techniques, str):
        try:
            wcag_techniques = json.loads(wcag_techniques)
        except json.JSONDecodeError:
            wcag_techniques = []

    records.append({
        "index": i,
        "file": entry.get("file"),
        "rule_id": entry.get("rule_id"),
        "violation_count": len(entry.get("nodes", [])),
        "html": entry.get("html"),
        "impact": entry.get("impact"),
        "target_selector": entry.get("target"),
        "wcag_technique": "; ".join([t.get("id", "") for t in wcag_techniques]),
        "html_file_path": entry.get("html_file_path"),
        "violation_count_in_file": file_counts[entry.get("file", "")]
    })

# === Save to CSV ===
df = pd.DataFrame(records)
df.to_csv("pre_fix_violation_summary.csv", index=False)
print("✅ Violation summary saved with file-level violation counts.")
