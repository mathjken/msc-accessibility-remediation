import pandas as pd
from scipy.stats import shapiro, ttest_rel, wilcoxon
from numpy import mean, std
import numpy as np

# Load the fix success scores CSV
df = pd.read_csv("fix_success_scores.csv")

# Extract scores
cot_scores = df["cot_score"]
rag_scores = df["rag_score"]

# Shapiro-Wilk normality test
shapiro_cot = shapiro(cot_scores)
shapiro_rag = shapiro(rag_scores)

print("Shapiro-Wilk Test:")
print(f"  CoT p-value: {shapiro_cot.pvalue:.4f}")
print(f"  RAG p-value: {shapiro_rag.pvalue:.4f}")

normality = shapiro_cot.pvalue > 0.05 and shapiro_rag.pvalue > 0.05
print("✅ Data is normally distributed" if normality else "⚠️ Data is not normally distributed")

# Paired t-test or Wilcoxon signed-rank test
print("\nPaired Statistical Test:")
if normality:
    t_stat, p_val = ttest_rel(cot_scores, rag_scores)
    test_used = "Paired t-test"
else:
    w_stat, p_val = wilcoxon(cot_scores, rag_scores)
    test_used = "Wilcoxon signed-rank test"

print(f"✅ {test_used} p-value: {p_val:.4f}")

# Compute Cohen's d for effect size with check for std == 0
def cohens_d(a, b):
    diff = np.array(a) - np.array(b)
    std_diff = np.std(diff, ddof=1)
    return 0.0 if std_diff == 0 else np.mean(diff) / std_diff

d = cohens_d(cot_scores, rag_scores)
print(f"\n📏 Cohen's d: {d:.4f} (effect size)")

# Prepare output summary
output_summary = {
    "Shapiro CoT p": [shapiro_cot.pvalue],
    "Shapiro RAG p": [shapiro_rag.pvalue],
    "Normality": ["Yes" if normality else "No"],
    "Test Used": [test_used],
    "p-value": [p_val],
    "Cohen's d": [d]
}

# Save to CSV
summary_df = pd.DataFrame(output_summary)
summary_df.to_csv("statistical_analysis_summary.csv", index=False)

print("\n📄 Results saved to: statistical_analysis_summary.csv")
