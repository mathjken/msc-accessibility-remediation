import json
import html
import re
from bs4 import BeautifulSoup

# === Self-closing tag fixer ===
def fix_self_closing_tags(html_str: str) -> str:
    void_elements = [
        "area", "base", "br", "col", "embed", "hr", "img",
        "input", "link", "meta", "source", "track", "wbr"
    ]
    for tag in void_elements:
        html_str = re.sub(fr"<{tag}([^/>]*?)>", fr"<{tag}\1 />", html_str)
    return html_str

# === Auto-fix unclosed tags using BeautifulSoup ===
def sanitize_html(html_snippet: str) -> str:
    try:
        soup = BeautifulSoup(html_snippet, "html.parser")
        return str(soup)
    except Exception:
        return html_snippet  # Fallback if BeautifulSoup fails

# === Load JSON output from CoT and RAG ===
with open("results_cot_rag_generated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# === Generate HTML blocks for each fix ===
html_blocks = []
for i, row in enumerate(data):
    original_html = html.escape(row.get("html", "").strip())
    cot_raw = row.get("cot_response", "").strip()
    rag_raw = row.get("rag_response", "").strip()
    file_name = row.get("file", f"snippet_{i+1}")

    # Sanitize and wrap CoT and RAG if needed
    cot_response = sanitize_html(cot_raw)
    rag_response = sanitize_html(rag_raw)

    if not cot_response.strip().startswith("<"):
        cot_response = f"<div>{cot_response}</div>"
    if not rag_response.strip().startswith("<"):
        rag_response = f"<div>{rag_response}</div>"

    html_blocks.append(f"""
    <section style="border:1px solid #ccc; padding:15px; margin:15px;">
      <h2>Fix #{i+1} - {file_name}</h2>

      <h3>🔧 Original HTML</h3>
      <pre style="background:#f4f4f4; padding:10px;">{original_html}</pre>

      <h3>🧠 CoT Fixed HTML (Ready for Axe Scan)</h3>
      <section data-source="cot" style="background:#fff7e6; padding:10px; border:1px dashed #aaa;">
        {cot_response}
      </section>

      <h3>✅ RAG Fixed HTML (Ready for Axe Scan)</h3>
      <section data-source="rag" style="background:#f6ffed; padding:10px; border:1px dashed #ccc;">
        {rag_response}
      </section>
    </section>
    """)

# === Combine all into full HTML page ===
full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>WCAG Fix Viewer</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    h2 {{ color: #333; }}
    pre {{ white-space: pre-wrap; word-break: break-word; }}
  </style>
</head>
<body>
  <h1>🔍 WCAG Accessibility Fix Review</h1>
  <main id="axe-scan-target">
    {"".join(html_blocks)}
  </main>
</body>
</html>
"""

# === Ensure self-closing void tags are correct ===
full_html = fix_self_closing_tags(full_html)

# === Save final output ===
with open("fix_review_dual.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("✅ Dual HTML report with CoT + RAG fixes saved to: fix_review_dual.html")
