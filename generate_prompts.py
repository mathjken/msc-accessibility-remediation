import os
import json
import pandas as pd

# === Input/Output Paths ===
input_file = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\violations_urls_critical_sampled_20percent.csv"
output_file = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\prompts_cot_rag.csv"

# === Load CSV ===
df = pd.read_csv(input_file)
df.fillna("", inplace=True)
sampled_df = df.copy()  # No sampling applied

# === Rule-specific fix hints
FIX_HINTS = {
    "button-name": "Add inner text or use aria-label for screen reader accessibility.",
    "aria-required-parent": "Ensure the element is within the correct ARIA parent structure.",
    "aria-label": "Add a descriptive aria-label attribute to the element.",
    "aria-labelledby": "Reference an existing descriptive element using aria-labelledby.",
}

# === Prompt Generation ===
prompt_rows = []

for _, row in sampled_df.iterrows():
    html = row.get("html", "").strip()
    rule_id = row.get("rule_id", "")
    wcag_url = row.get("wcag_url") or "https://www.w3.org/WAI/WCAG22/"
    wcag_guideline = row.get("wcag_guideline") or "4.1.2"
    wcag_description = row.get("wcag_description") or "Name, Role, Value"
    file = row.get("file", "")
    html_file_path = row.get("html_file_path", "")
    impact = row.get("impact", "")

    # === Techniques
    techniques_raw = row.get("wcag_techniques", "")
    techniques_list = ""
    if isinstance(techniques_raw, str):
        try:
            techniques = json.loads(techniques_raw)
            techniques_list = ", ".join([t["id"] for t in techniques])
        except:
            techniques_list = techniques_raw

    # === Failure Summary (max 5 lines)
    issue_list = []
    nodes = row.get("nodes", "")
    try:
        nodes_data = json.loads(nodes)
        for node in nodes_data:
            summary = node.get("failureSummary", "")
            if summary:
                for line in summary.split("\n"):
                    line = line.strip()
                    if line and not line.lower().startswith("fix any of"):
                        issue_list.append(line)
    except Exception as e:
        print(f" Failed to parse nodes for {file}: {e}")

    issue_list = list(set(issue_list))[:5]  # Deduplicate + limit to 5
    issues_text = "\n- " + "\n- ".join(issue_list) if issue_list else "No specific failure details provided."
    fix_hint = FIX_HINTS.get(rule_id, "Refer to WCAG techniques and failure summary for fix guidance.")
    prompt_context = f"```html\n{html}\n```"

    # === Compact Chain-of-Thought Prompt
    cot_prompt = (
        f"HTML flagged under WCAG 2.2 SC {wcag_guideline} - {wcag_description} (rule ID: {rule_id}):\n"
        f"Issues:{issues_text}\n\n"
        f"Techniques: {techniques_list}\n"
        f"Hint: {fix_hint}\n\n"
        f"Fix this:\n{prompt_context}"
    )

    # === Compact Retrieval-Augmented Prompt
    rag_prompt = (
        f"This HTML violates WCAG 2.2 SC {wcag_guideline} - {wcag_description} (rule ID: {rule_id}).\n"
        f"Issues:{issues_text}\n\n"
        f"Refer to: {wcag_url} | Techniques: {techniques_list}\n"
        f"Hint: {fix_hint}\n\n"
        f"Return only fixed HTML:\n{prompt_context}"
    )

    # === Store prompts
    prompt_rows.append({
        "file": file,
        "rule_id": rule_id,
        "html_file_path": html_file_path,
        "html": html,
        "wcag_guideline": wcag_guideline,
        "wcag_description": wcag_description,
        "wcag_url": wcag_url,
        "wcag_techniques": techniques_list,
        "impact": impact,
        "cot_prompt": cot_prompt,
        "rag_prompt": rag_prompt
    })

# === Save CSV ===
prompt_df = pd.DataFrame(prompt_rows)
prompt_df.to_csv(output_file, index=False, quoting=1)

print("✅ Prompt generation complete.")
print(f"📄 Saved to {output_file}")
