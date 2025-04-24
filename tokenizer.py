import pandas as pd
import tiktoken

df = pd.read_csv("prompts_cot_rag_mapped.csv")
tokenizer = tiktoken.encoding_for_model("gpt-4")

df["cot_tokens"] = df["cot_prompt"].apply(lambda x: len(tokenizer.encode(str(x))))
df["rag_tokens"] = df["rag_prompt"].apply(lambda x: len(tokenizer.encode(str(x))))
df["total_tokens"] = df["cot_tokens"] + df["rag_tokens"]

print(df[["file", "cot_tokens", "rag_tokens", "total_tokens"]].head())
print(f"Total tokens used: {df['total_tokens'].sum()}")
print(f"Avg tokens per prompt: {df['total_tokens'].mean()}")
