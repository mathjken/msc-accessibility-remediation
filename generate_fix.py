import os
import json
import pandas as pd
import tiktoken
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI

# === Load API key ===
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# === Relevant WCAG technique URLs ===
wcag_urls = [
    # SC 1.3.1 Techniques
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA11.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA12.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA13.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA17.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA20.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/html/H44.html",
    # SC 4.1.2 Techniques
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA14.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA16.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA5.html",
    "https://www.w3.org/WAI/WCAG22/Techniques/general/G108.html"
]

# === Load and chunk documentation ===
documents = []
for url in wcag_urls:
    print(f"📖 Loading WCAG page: {url}")
    loader = WebBaseLoader(url)
    documents.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(documents)

# === Embedding + Vector Store ===
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever()

# === Setup models ===
llm = ChatOpenAI(model_name="gpt-4", temperature=0)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# === Load prompt CSV and set tokenizer ===
df = pd.read_csv("prompts_cot_rag_mapped.csv")
tokenizer = tiktoken.encoding_for_model("gpt-4")

# === Initialize outputs ===
cot_responses, rag_responses, token_logs = [], [], []

# === Run for each row ===
for i, row in df.iterrows():
    try:
        print(f"\n🚧 Processing row {i} - Rule ID: {row['rule_id']}")

        # --- Use correct columns ---
        cot_prompt = row.get("cot_prompt", "")
        rag_prompt = row.get("rag_prompt", "")

        # --- Preview token usage ---
        cot_tokens = len(tokenizer.encode(str(cot_prompt)))
        rag_tokens = len(tokenizer.encode(str(rag_prompt)))
        total_tokens = cot_tokens + rag_tokens
        print(f"🧠 Token Estimate → CoT: {cot_tokens}, RAG: {rag_tokens}, Total: {total_tokens}")

        # --- Generate responses ---
        cot_response = llm.predict(cot_prompt)
        rag_response = qa_chain.run(rag_prompt)

    except Exception as e:
        print(f"❌ Error on row {i}: {e}")
        cot_response = f"ERROR: {e}"
        rag_response = f"ERROR: {e}"

    # --- Store results ---
    cot_responses.append(cot_response.strip())
    rag_responses.append(rag_response.strip())
    token_logs.append({
        "index": i,
        "rule_id": row["rule_id"],
        "cot_tokens": cot_tokens,
        "rag_tokens": rag_tokens,
        "total_tokens": total_tokens
    })

# === Save outputs ===
df["cot_response"] = cot_responses
df["rag_response"] = rag_responses

df.to_csv("results_cot_rag_generated.csv", index=False)
df.to_json("results_cot_rag_generated.json", orient="records", indent=2, force_ascii=False)

with open("token_summary.json", "w", encoding="utf-8") as f:
    json.dump(token_logs, f, indent=2)

print("\n✅ All results saved to:")
print("  → results_cot_rag_generated.csv")
print("  → results_cot_rag_generated.json")
print("  → token_summary.json")