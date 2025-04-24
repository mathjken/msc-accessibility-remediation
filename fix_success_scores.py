import pandas as pd

# Load your dual fix comparison file
df = pd.read_csv("violation_fix_comparison_dual.csv")

# Keep only relevant columns
df = df[["rule_id", "source_file", "fix_status"]]

# Convert fix_status to binary score
df["score"] = df["fix_status"].apply(lambda x: 1 if "✅" in x else 0)

# Pivot to have one row per rule_id, with CoT and RAG scores as columns
pivot_df = df.pivot_table(index="rule_id", columns="source_file", values="score", fill_value=0).reset_index()

# Rename columns clearly
pivot_df.columns.name = None
pivot_df = pivot_df.rename(columns={"cot": "cot_score", "rag": "rag_score"})

# Save to CSV
pivot_df.to_csv("fix_success_scores.csv", index=False)
print("✅ fix_success_scores.csv created.")
