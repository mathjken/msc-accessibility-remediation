import json
import csv

# === Load your clustered and mapped JSON file ===
input_file = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\clustered_violations_mapped.json"
output_csv = "prompts_cot_rag_mapped.csv"
output_json = "prompts_cot_rag_mapped.json"

# === Rule-specific explanations for pseudo-retrieval ===
rule_descriptions = {
    "aria-required-children": "This issue typically occurs when a container element with a required role is missing its expected child roles (e.g., <ul role='menu'> should contain <li role='menuitem'>).",
    "aria-valid-attr-value": "This issue typically arises when ARIA attributes contain values not allowed by the ARIA specification.",
    "aria-allowed-attr": "This issue usually occurs when a non-permissible ARIA attribute is used on an element where it’s not valid.",
    "aria-label": "This issue happens when elements meant to be labeled for assistive technologies are missing descriptive labels.",
    "button-name": "This issue occurs when a <button> lacks accessible text content or an accessible name.",
    "aria-labelledby": "This issue happens when the referenced ID in aria-labelledby does not match any element or is missing."
    # Add more as needed
}

with open(input_file, "r", encoding="utf-8") as f:
    violations = json.load(f)

# === Build CoT and RAG prompts ===
rows = []
for v in violations:
    html = v.get("html", "").strip()
    rule_id = v.get("rule_id", "")
    wcag_id = v.get("wcag_guideline", "")
    wcag_desc = v.get("wcag_description", "")
    file = v.get("file", "")
    techniques = v.get("wcag_techniques", [])

    # Lookup known issue cause
    issue_cause = rule_descriptions.get(rule_id, "This issue typically involves accessibility requirements related to the structure or attributes of the HTML element.")

    # 🔹 CoT Prompt: Explain and Fix
    cot_prompt = f"""You are an accessibility expert. Analyze the following HTML for accessibility issues related to WCAG {wcag_id} ({wcag_desc}).
Issue: {rule_id}
HTML: {html}
Step-by-step reasoning: Explain what is wrong, why it violates WCAG, and provide an updated HTML fix to resolve the issue."""

    # 🔹 RAG Prompt: Enriched with issue and technique context
    techniques_str = "\n".join([f"- {t['id']}: {t['desc']}" for t in techniques])
    rag_prompt = f"""Fix the following HTML snippet which violates WCAG {wcag_id} ({wcag_desc}).
Issue: {rule_id} — {issue_cause}

HTML: {html}

Apply the following WCAG techniques:
{techniques_str}

Generate only the updated HTML version that complies with WCAG."""

    rows.append({
        "file": file,
        "rule_id": rule_id,
        "wcag_guideline": wcag_id,
        "wcag_description": wcag_desc,
        "html": html,
        "cot_prompt": cot_prompt,
        "rag_prompt": rag_prompt
    })

# === Save to CSV ===
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "file", "rule_id", "wcag_guideline", "wcag_description", "html", "cot_prompt", "rag_prompt"
    ])
    writer.writeheader()
    writer.writerows(rows)

# === Save to JSON ===
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

print("✅ Done! Fix-oriented CoT + RAG prompts saved to:")
print("-", output_csv)
print("-", output_json)
