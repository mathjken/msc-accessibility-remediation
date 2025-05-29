import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_rel, shapiro, wilcoxon, f_oneway

# === Load Evaluation Data ===
df = pd.read_csv("Fix_Evaluation_Table.csv")

# === Clean and Prepare ===
df = df.dropna(subset=["cot_compliance_score", "rag_compliance_score", "original_violation_count"])
df["cot_compliance_score"] = pd.to_numeric(df["cot_compliance_score"], errors="coerce")
df["rag_compliance_score"] = pd.to_numeric(df["rag_compliance_score"], errors="coerce")

# === Compute Fix Success Rate ===
cot_success_rate = (df["cot_compliance_score"] > 0).mean() * 100
rag_success_rate = (df["rag_compliance_score"] > 0).mean() * 100

# === Compute New Violation Rate ===
df["cot_new_violation"] = df["cot_violation_count"] > df["original_violation_count"]
df["rag_new_violation"] = df["rag_violation_count"] > df["original_violation_count"]
cot_new_violation_rate = df["cot_new_violation"].mean() * 100
rag_new_violation_rate = df["rag_new_violation"].mean() * 100

# === Statistical Analysis ===
shapiro_cot = shapiro(df["cot_compliance_score"])
shapiro_rag = shapiro(df["rag_compliance_score"])
t_stat, t_p = ttest_rel(df["cot_compliance_score"], df["rag_compliance_score"])
wilcoxon_stat, wilcoxon_p = wilcoxon(df["cot_compliance_score"], df["rag_compliance_score"])
anova_stat, anova_p = f_oneway(df["original_violation_count"],
                               df["cot_violation_count"],
                               df["rag_violation_count"])

# === Cohen’s d ===
diff = df["rag_compliance_score"] - df["cot_compliance_score"]
cohens_d = diff.mean() / diff.std()

# === Print Summary ===
print("=== Evaluation Summary ===")
print(f"CoT Fix Success Rate: {cot_success_rate:.2f}%")
print(f"RAG Fix Success Rate: {rag_success_rate:.2f}%")
print(f"CoT New Violation Rate: {cot_new_violation_rate:.2f}%")
print(f"RAG New Violation Rate: {rag_new_violation_rate:.2f}%")
print(f"Shapiro-Wilk (CoT) p = {shapiro_cot.pvalue:.4f}")
print(f"Shapiro-Wilk (RAG) p = {shapiro_rag.pvalue:.4f}")
print(f"T-Test p = {t_p:.4f}")
print(f"Wilcoxon p = {wilcoxon_p:.4f}")
print(f"ANOVA p = {anova_p:.4f}")
print(f"Cohen’s d = {cohens_d:.2f}")

# === Visualizations ===
output_dir = "eval_charts"
os.makedirs(output_dir, exist_ok=True)

# Boxplot of Compliance Scores
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[["cot_compliance_score", "rag_compliance_score"]])
plt.title("Boxplot of Compliance Scores")
plt.ylabel("Compliance Score")
plt.savefig(os.path.join(output_dir, "boxplot_compliance_scores.png"))
plt.close()

# Fix Success Rate Barplot
plt.figure(figsize=(8, 6))
sns.barplot(x=["CoT", "RAG"], y=[cot_success_rate, rag_success_rate])
plt.title("Fix Success Rate")
plt.ylabel("Success Rate (%)")
plt.savefig(os.path.join(output_dir, "barplot_fix_success_rate.png"))
plt.close()

# New Violation Rate Barplot
plt.figure(figsize=(8, 6))
sns.barplot(x=["CoT", "RAG"], y=[cot_new_violation_rate, rag_new_violation_rate])
plt.title("New Violation Rate")
plt.ylabel("New Violation Rate (%)")
plt.savefig(os.path.join(output_dir, "barplot_new_violation_rate.png"))
plt.close()

print(f"\nCharts saved in: {output_dir}")
