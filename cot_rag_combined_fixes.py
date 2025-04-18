import json
import os
import csv
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Initialize OpenAI LLM (gpt-4-1106-preview is more stable and widely accessible)
llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4-1106-preview", temperature=0)

# ✅ Paths and filenames
base_dir = os.path.join("C:/", "Users", "ogujo", "OneDrive - Northumbria University - Production Azure AD", "MSC PROJECT", "1000study", "data")
input_path = os.path.join(base_dir, "sampled_kmeans_violations.json")
output_json = "cot_rag_combined_fixes.json"
output_csv = "cot_rag_combined_fixes.csv"

# ✅ Load sampled violations
with open(input_path, "r", encoding="utf-8") as f:
    samples = json.load(f)

# ✅ WCAG context string for RAG
wcag_reference = """
According to WCAG 2.2 SC 4.1.2 and SC 1.3.1, HTML elements must expose their name, role, and value to assistive technologies.
Elements that serve a functional role (e.g., buttons, links, checkboxes) should have accessible names using <aria-label>, <aria-labelledby>, or native HTML labeling.
Incorrect or missing roles, improper ARIA attributes, and unlabeled interactive components hinder screen reader usability.
"""

# ✅ Define prompt templates
cot_prompt = PromptTemplate(
    input_variables=["html", "rule_id"],
    template="""
You are an accessibility expert. Given the following HTML snippet:

{html}

The accessibility rule violated is: {rule_id}

Step-by-step, explain why this violates WCAG 2.2, then suggest a corrected version of the HTML that is fully accessible.
"""
)

rag_prompt = PromptTemplate(
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

# ✅ Collect results
combined_results = []

for item in tqdm(samples, desc="🔁 Generating CoT and RAG fixes"):
    html = item.get("html", "").strip()
    rule_id = item.get("rule_id", "")

    if not html:
        continue  # Skip empty HTML snippets

    # 🧠 CoT fix
    cot_input = cot_prompt.format(html=html, rule_id=rule_id)
    cot_response = llm.invoke(cot_input)

    # 📚 RAG fix
    rag_input = rag_prompt.format(html=html, rule_id=rule_id, doc=wcag_reference)
    rag_response = llm.invoke(rag_input)

    combined_results.append({
        "original_html": html,
        "rule_id": rule_id,
        "fix_cot": cot_response.content,
        "fix_rag": rag_response.content
    })

# ✅ Save results to JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(combined_results, f, indent=2)

# ✅ Save results to CSV
with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["original_html", "rule_id", "fix_cot", "fix_rag"])
    writer.writeheader()
    for row in combined_results:
        writer.writerow(row)

print("✅ Combined CoT and RAG fix generation complete!")
print(f"📝 JSON: {output_json}")
print(f"📄 CSV : {output_csv}")