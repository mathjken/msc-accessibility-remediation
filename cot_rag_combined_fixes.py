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

# ✅ Initialize OpenAI LLM
llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4", temperature=0.3)

# ✅ Load sampled violations
input_path = "C:/Users/w23063958/OneDrive - Northumbria University - Production Azure AD/MSC PROJECT/1000study/data/sampled_kmeans_violations.json"
with open(input_path, "r", encoding="utf-8") as f:
    samples = json.load(f)

# ✅ WCAG reference for RAG (injected context)
wcag_reference = """
According to WCAG 2.2 SC 4.1.2 and SC 1.3.1, HTML elements should include appropriate ARIA attributes, labels, and roles that are programmatically determinable. Interactive elements must be properly named and structured to ensure compatibility with assistive technologies.
"""

# ✅ Prompt Templates
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

# ✅ Result containers
combined_results = []
output_json = "cot_rag_combined_fixes.json"
output_csv = "cot_rag_combined_fixes.csv"

# ✅ Run both CoT and RAG for each sample
for item in tqdm(samples, desc="🔁 Running CoT and RAG"):
    html = item["html"]
    rule_id = item["rule_id"]

    # CoT response
    cot_text = cot_prompt.format(html=html, rule_id=rule_id)
    cot_fix = llm.predict(cot_text)

    # RAG response
    rag_text = rag_prompt.format(html=html, rule_id=rule_id, doc=wcag_reference)
    rag_fix = llm.predict(rag_text)

    combined_results.append({
        "original_html": html,
        "rule_id": rule_id,
        "fix_cot": cot_fix,
        "fix_rag": rag_fix
    })

# ✅ Save combined results to JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(combined_results, f, indent=2)

# ✅ Save combined results to CSV
with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["original_html", "rule_id", "fix_cot", "fix_rag"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in combined_results:
        writer.writerow(row)

print("✅ Combined CoT and RAG fix generation complete!")
print(f"Saved to: {output_json} and {output_csv}")
