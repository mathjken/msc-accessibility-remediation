import json
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load env variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI LLM
llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4", temperature=0)

# Load your sampled file (KMeans example)
with open("C:/Users/w23063958/OneDrive - Northumbria University - Production Azure AD/MSC PROJECT/1000study/data/sampled_kmeans_violations.json", "r", encoding="utf-8") as f:
    samples = json.load(f)

# Example prompt template (Chain-of-Thought)
cot_template = PromptTemplate(
    input_variables=["html", "rule_id"],
    template="""
You are an accessibility expert. Given the following HTML snippet:

{html}

The accessibility rule violated is: {rule_id}

Step-by-step, explain why this violates WCAG 2.2, then suggest a corrected version of the HTML that is fully accessible.
"""
)

# Loop through samples and call GPT-4
results = []
for item in samples:
    html = item["html"]
    rule_id = item["rule_id"]
    
    # Build prompt using CoT template
    prompt = cot_template.format(html=html, rule_id=rule_id)
    
    # Get response from GPT-4
    response = llm.predict(prompt)
    
    # Store results
    results.append({
        "original_html": html,
        "rule_id": rule_id,
        "fix_cot": response
    })

# Save result to JSON
with open("cot_fixes.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("✅ CoT fix generation complete!")
