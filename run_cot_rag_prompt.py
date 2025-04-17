import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ✅ Load OpenAI key securely from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ✅ Initialize the LLM
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.3,
    openai_api_key=api_key
)

# === EXAMPLE HTML VIOLATION INPUT (replace with your actual snippet) ===
html_snippet = """
<button class="btn">Click here</button>
"""

rule_id = "button-name"
wcag_sc = "SC 4.1.2 - Name, Role, Value"

# ✅ 1. Chain-of-Thought (CoT) Prompt Template
cot_prompt = PromptTemplate(
    input_variables=["html", "rule", "sc"],
    template="""
You are an expert in web accessibility and WCAG 2.2 remediation. You are given an HTML snippet that has a critical accessibility violation.

Violation Details:
Rule: {rule}
WCAG SC: {sc}

HTML Snippet:
{html}

Step by step, explain the accessibility problem, and generate a fully fixed, WCAG-compliant HTML replacement. Make sure the fix includes descriptive text and follows accessibility best practices.
"""
)

cot_chain = LLMChain(llm=llm, prompt=cot_prompt)
cot_result = cot_chain.run({
    "html": html_snippet,
    "rule": rule_id,
    "sc": wcag_sc
})

print("\n🧠 Chain-of-Thought Fix:")
print(cot_result)


# ✅ 2. Retrieval-Augmented Generation (RAG) Prompt Template
# Simulating retrieval by injecting external context (in real case, use retriever)
wcag_reference = """
According to WCAG 2.2 SC 4.1.2, interactive components like buttons must have accessible names that describe their purpose. For example, <button>Learn more</button> is not descriptive, but <button>View product details</button> is better.
"""

rag_prompt = PromptTemplate(
    input_variables=["html", "rule", "sc", "doc"],
    template="""
You are an accessibility expert with access to real-time WCAG documentation.

Violation Details:
Rule: {rule}
WCAG SC: {sc}

Retrieved Documentation:
{doc}

HTML Snippet:
{html}

Based on the WCAG guidance above, fix the HTML snippet to meet accessibility standards. Provide the corrected HTML and explain your changes.
"""
)

rag_chain = LLMChain(llm=llm, prompt=rag_prompt)
rag_result = rag_chain.run({
    "html": html_snippet,
    "rule": rule_id,
    "sc": wcag_sc,
    "doc": wcag_reference
})

print("\n📚 RAG Fix (with WCAG context):")
print(rag_result)
