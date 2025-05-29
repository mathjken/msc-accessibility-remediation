import pandas as pd

# === File Paths ===
pre_file = "pre_fix_violation_summary.csv"
grouped_file = "Grouped_Violations_with_HTML_Column.xlsx"
output_file = "Fix_Evaluation_Table.csv"

# === Load Data ===
pre_df = pd.read_csv(pre_file)
grouped_df = pd.read_excel(grouped_file)

# === Normalize filenames
pre_df["file"] = pre_df["file"].astype(str).str.strip().str.lower()
grouped_df["file"] = grouped_df["file"].astype(str).str.strip().str.lower()

# === Pivot grouped_df on 'fix_type' and 'file'
pivoted = grouped_df.pivot(index="file", columns="fix_type", values=["violation_count", "cot_response", "rag_response", "html"])
pivoted.columns = ['_'.join(col).lower() for col in pivoted.columns]
pivoted = pivoted.reset_index()

# === Merge with pre_df using 'file'
merged = pd.merge(pre_df, pivoted, on="file", how="inner")

# === Compute Compliance
merged["cot_compliance_score"] = (merged["violation_count"] - merged["violation_count_cot"]) / merged["violation_count"]
merged["rag_compliance_score"] = (merged["violation_count"] - merged["violation_count_rag"]) / merged["violation_count"]
merged["cot_improved"] = merged["violation_count_cot"] < merged["violation_count"]
merged["rag_improved"] = merged["violation_count_rag"] < merged["violation_count"]

# === Final Output
evaluation_table = merged[[ 
    "file",
    "rule_id",
    "html",                  # before fix
    "html_cot",              # after CoT
    "html_rag",              # after RAG
    "cot_response_cot",
    "rag_response_rag",
    "violation_count",       # original
    "violation_count_cot",
    "violation_count_rag",
    "cot_compliance_score",
    "rag_compliance_score",
    "cot_improved",
    "rag_improved"
]].rename(columns={
    "html": "before_html",
    "violation_count": "original_violation_count",
    "violation_count_cot": "cot_violation_count",
    "violation_count_rag": "rag_violation_count",
    "cot_response_cot": "cot_response",
    "rag_response_rag": "rag_response",
    "html_cot": "after_html_cot",
    "html_rag": "after_html_rag"
})

# === Add Manual Review Placeholders
evaluation_table["manual_score"] = ""
evaluation_table["correctness"] = ""
evaluation_table["completeness"] = ""

# === Save to CSV
evaluation_table.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")
