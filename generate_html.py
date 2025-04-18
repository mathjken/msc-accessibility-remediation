import json
import os

# Load fixes
with open("cot_rag_combined_fixes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Output folder
os.makedirs("html_snippets", exist_ok=True)

# HTML template
template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Fix Test</title>
</head>
<body>
  {html}
</body>
</html>
"""

# Generate HTML files
for i, item in enumerate(data):
    cot_html = template.format(html=item["fix_cot"])
    rag_html = template.format(html=item["fix_rag"])

    with open(f"html_snippets/fix_cot_{i}.html", "w", encoding="utf-8") as f:
        f.write(cot_html)

    with open(f"html_snippets/fix_rag_{i}.html", "w", encoding="utf-8") as f:
        f.write(rag_html)

print("✅ Standalone HTML files created in the 'html_snippets/' folder.")
