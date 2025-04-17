import json
import os
import csv
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tqdm import tqdm

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Initialize LLM
llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4", temperature=0)

# ✅ Load sampled violations
input_path = "C:/Users/w23063958/OneDrive - Northumbria University - Production Azure AD/MSC PROJECT/1000study/data/sampled_kmeans_violations.json"
with open(input_path, "r", encoding="utf-8") as f:
    samples = json.load(f)

# ✅ Prompt Template for RAG
rag_template = PromptTemplate(
    input_variables=["html", "rule_id", "doc"],
    template="""
You are an accessibility expert. Given the following HTML snippet:

{html}

The accessibility rule violated is: {rule_id}

Based on the WCAG documentation provided below:
{doc}

Fix the HTML to comply with WCAG standards. Provide a corrected HTML and briefly explain what was changed.
"""
)

# ✅ Injected WCAG reference (replaceable later with dynamic retrieval)
wcag_reference = """
According to WCAG 2.2 SC 4.1.2 and SC 1.3.1, HTML elements should include appropriate ARIA attributes, labels, and roles that are programmatically determinable. Interactive elements must be properly named and structured to ensure compatibility with assistive technologies.
"""

# ✅ Results container
results = []
output_json = "rag_fixes.json"
output_csv = "rag_fixes.csv"

# ✅ Loop through violations
for item in tqdm(samples, desc="🔧 Generating RAG Fixes"):
    html = item["html"]
    rule_id = item["rule_id"]

    prompt = rag_template.format(html=html, rule_id=rule_id, doc=wcag_reference)
    response = llm.predict(prompt)

    results.append({
        "original_html": html,
        "rule_id": rule_id,
        "fix_rag": response
    })

# ✅ Save to JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

# ✅ Save to CSV
with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["original_html", "rule_id", "fix_rag"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print("✅ RAG fix generation complete!")
print(f"Saved to: {output_json} and {output_csv}")
