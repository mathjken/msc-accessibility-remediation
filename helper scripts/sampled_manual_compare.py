import pandas as pd

# Load the CSV file
df = pd.read_csv("manual_comparison_old_new.csv")

# Filter rows that have at least one rule_id (i.e., valid violations)
filtered_df = df[df["rule_id"].notna() & df["rule_id"].str.strip().ne("")]

# Randomly sample up to 20 rows
sampled_df = filtered_df.sample(n=min(20, len(filtered_df)), random_state=42)

# Select and reorder the desired columns
columns = [
    "id", "rule_id", "original_html", "cot_fixed_html", "rag_fixed_html",
    "fix_completeness", "fix_correctness", "wcag_alignment", "comments"
]
sampled_df = sampled_df[columns]

# Save to a new CSV file or display
sampled_df.to_csv("sampled_manual_comparison_table.csv", index=False)
print("✅ Sampled table saved to 'sampled_manual_comparison_table.csv'")
