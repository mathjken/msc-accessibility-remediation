import pandas as pd
import json

# === Load CSV ===
input_csv = "results_cot_rag_generated.csv"
df = pd.read_csv(input_csv)

# === Save full JSON from CSV ===
full_json_output = "results_cot_rag_generated.json"
df.to_json(full_json_output, orient="records", indent=2, force_ascii=False)
print(f"✅ Full CSV converted to JSON → {full_json_output}")

# === Create simplified fixes JSON output ===
fixes = []
for _, row in df.iterrows():
    fixes.append({
        "file": row.get("file", ""),
        "rule_id": row.get("rule_id", ""),
        "wcag_guideline": row.get("wcag_guideline", ""),
        "original_html": row.get("html", ""),
        "cot_fix": row.get("cot_response", ""),
        "rag_fix": row.get("rag_response", "")
    })

fixes_output_path = "fixes_output.json"
with open(fixes_output_path, "w", encoding="utf-8") as f:
    json.dump(fixes, f, indent=2, ensure_ascii=False)

print(f"✅ Fixes exported to simplified JSON → {fixes_output_path}")
