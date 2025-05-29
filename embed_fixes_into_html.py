import os
import json
import pandas as pd
from bs4 import BeautifulSoup

# === Paths ===
input_file = r"results_cot_rag_generated.json"
output_dir = os.path.join(os.path.dirname(input_file), "html_fixes_embedded")
os.makedirs(output_dir, exist_ok=True)
fail_log = []
success_log = []

# === Load JSON ===
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# === Utilities ===
def approximate_match(soup, snippet):
    snippet_tag = BeautifulSoup(snippet, "html.parser").find()
    if not snippet_tag:
        return None

    tag_name = snippet_tag.name
    id_val = snippet_tag.get("id")
    role_val = snippet_tag.get("role")
    aria_attrs = {k: v for k, v in snippet_tag.attrs.items() if k.startswith("aria-")}

    candidates = soup.find_all(tag_name)
    for tag in candidates:
        if id_val and tag.get("id") == id_val:
            return tag
        if role_val and tag.get("role") == role_val:
            return tag
        if any(tag.get(k) == v for k, v in aria_attrs.items()):
            return tag
    return None

def wrap_fixed_html(fixed_html, data_source="cot"):
    return f'<section data-source="{data_source}">\n{fixed_html.strip()}\n</section>'

# === Process ===
for idx, row in enumerate(data):
    html_path = row.get("html_file_path", "")
    if not html_path or not os.path.isfile(html_path):
        fail_log.append({"index": idx, "reason": "Missing or invalid HTML file path"})
        continue

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            original_html = f.read()
        soup = BeautifulSoup(original_html, "html.parser")

        old_fragment = row.get("html", "")
        cot_fix = row.get("cot_response", "")
        rag_fix = row.get("rag_response", "")

        cot_section = BeautifulSoup(wrap_fixed_html(cot_fix, "cot"), "html.parser")
        rag_section = BeautifulSoup(wrap_fixed_html(rag_fix, "rag"), "html.parser")

        soup_cot = BeautifulSoup(str(soup), "html.parser")
        soup_rag = BeautifulSoup(str(soup), "html.parser")

        match_cot = approximate_match(soup_cot, old_fragment)
        match_rag = approximate_match(soup_rag, old_fragment)

        if match_cot:
            match_cot.replace_with(cot_section)
        else:
            soup_cot.body.append(cot_section)

        if match_rag:
            match_rag.replace_with(rag_section)
        else:
            soup_rag.body.append(rag_section)

        cot_path = os.path.join(output_dir, f"fix_cot_{idx}.html")
        rag_path = os.path.join(output_dir, f"fix_rag_{idx}.html")

        with open(cot_path, "w", encoding="utf-8") as f:
            f.write(str(soup_cot))
        with open(rag_path, "w", encoding="utf-8") as f:
            f.write(str(soup_rag))

        success_log.append({"index": idx, "cot_path": cot_path, "rag_path": rag_path})
        print(f"✅ Embedded fixes for row {idx}")

    except Exception as e:
        fail_log.append({"index": idx, "reason": str(e)})
        print(f"❌ Error on row {idx}: {e}")

# === Save logs
if fail_log:
    pd.DataFrame(fail_log).to_csv(os.path.join(output_dir, "embed_failures.csv"), index=False)
    print("⚠️ Failures logged to embed_failures.csv")

if success_log:
    pd.DataFrame(success_log).to_csv(os.path.join(output_dir, "embed_successes.csv"), index=False)
    print("✅ Successful embeddings logged to embed_successes.csv")

print(f"\n📁 All output saved to: {output_dir}")
