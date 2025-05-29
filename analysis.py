import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, wilcoxon, ttest_rel, f_oneway

def extract_likert_score(text, strategy):
    import re
    if not isinstance(text, str):
        return None
    text = text.replace('.', ',').replace('–', '-').replace('—', '-')
    pattern = fr"([0-2])-{strategy}"
    match = re.search(pattern, text.replace(" ", ""))
    return int(match.group(1)) if match else None

def calculate_likert_distribution(score_series):
    total = len(score_series)
    score_counts = score_series.value_counts().to_dict()
    return {
        "0 (Not Fixed)": round(score_counts.get(0, 0) / total * 100, 2),
        "1 (Partially Fixed)": round(score_counts.get(1, 0) / total * 100, 2),
        "2 (Fully WCAG-Compliant)": round(score_counts.get(2, 0) / total * 100, 2),
    }

def evaluate_fix_data(filepath):
    df = pd.read_excel(filepath, sheet_name="fix_evaluation_table")

    df["cot_completeness_score"] = df["completeness"].apply(lambda x: extract_likert_score(x, "COT"))
    df["rag_completeness_score"] = df["completeness"].apply(lambda x: extract_likert_score(x, "RAG"))
    df["cot_correctness_score"] = df["correctness"].apply(lambda x: extract_likert_score(x, "COT"))
    df["rag_correctness_score"] = df["correctness"].apply(lambda x: extract_likert_score(x, "RAG"))

    aligned_df = df.dropna(subset=["cot_violation_count", "rag_violation_count", "cot_compliance_score", "rag_compliance_score"])

    results = {}

    results["Fix Success Rate (%)"] = {
        "CoT": round(((df["cot_violation_count"] < df["original_violation_count"]) & df["cot_violation_count"].notna()).sum() / len(df) * 100, 2),
        "RAG": round(((df["rag_violation_count"] < df["original_violation_count"]) & df["rag_violation_count"].notna()).sum() / len(df) * 100, 2)
    }

    results["New Violations Introduced (%)"] = {
        "CoT": round(((df["cot_violation_count"] > df["original_violation_count"]) & df["cot_violation_count"].notna()).sum() / len(df) * 100, 2),
        "RAG": round(((df["rag_violation_count"] > df["original_violation_count"]) & df["rag_violation_count"].notna()).sum() / len(df) * 100, 2)
    }

    results["Average Compliance Score"] = {
        "CoT": round(df["cot_compliance_score"].mean(), 2),
        "RAG": round(df["rag_compliance_score"].mean(), 2)
    }

    results["Manual Score Distribution"] = {
        "Fix Completeness (%)": {
            "CoT": calculate_likert_distribution(df["cot_completeness_score"]),
            "RAG": calculate_likert_distribution(df["rag_completeness_score"])
        },
        "Fix Appropriateness (%)": {
            "CoT": calculate_likert_distribution(df["cot_correctness_score"]),
            "RAG": calculate_likert_distribution(df["rag_correctness_score"])
        }
    }

    results["Statistical Testing"] = {
        "Shapiro-Wilk p-values": {
            "CoT Compliance Score": round(shapiro(aligned_df["cot_compliance_score"]).pvalue, 4),
            "RAG Compliance Score": round(shapiro(aligned_df["rag_compliance_score"]).pvalue, 4)
        },
        "Wilcoxon p-value (Compliance Score)": round(wilcoxon(aligned_df["cot_compliance_score"], aligned_df["rag_compliance_score"]).pvalue, 4),
        "T-Test p-value (Compliance Score)": round(ttest_rel(aligned_df["cot_compliance_score"], aligned_df["rag_compliance_score"]).pvalue, 4)
    }

    anova_data = aligned_df.dropna(subset=["original_violation_count", "cot_violation_count", "rag_violation_count"])
    results["ANOVA p-value (Violations)"] = round(f_oneway(anova_data["original_violation_count"], anova_data["cot_violation_count"], anova_data["rag_violation_count"]).pvalue, 4)

    # Visualization
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=aligned_df[["cot_compliance_score", "rag_compliance_score"]])
    plt.title("Compliance Score Distribution")
    plt.ylabel("Score")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("compliance_score_boxplot.png")

    plt.figure(figsize=(8, 5))
    sns.barplot(x=["Original", "CoT", "RAG"], y=[
        anova_data["original_violation_count"].mean(),
        anova_data["cot_violation_count"].mean(),
        anova_data["rag_violation_count"].mean()
    ])
    plt.title("Average Violation Count")
    plt.ylabel("Count")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("average_violation_barplot.png")

    long_df = pd.melt(anova_data[["original_violation_count", "cot_violation_count", "rag_violation_count"]],
                      var_name="Fix Type", value_name="Violation Count")
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=long_df, x="Fix Type", y="Violation Count")
    plt.title("Violation Count: Original vs CoT vs RAG")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("violation_count_boxplot.png")

    return results

import json

if __name__ == "__main__":
    results = evaluate_fix_data("fix_evaluation_table.xlsx")

    # Print to console
    for section, content in results.items():
        print(f"\\n--- {section} ---")
        if isinstance(content, dict):
            for k, v in content.items():
                print(f"{k}: {v}")
        else:
            print(content)

    # Save results to JSON
    with open("evaluation_results.json", "w") as f_json:
        json.dump(results, f_json, indent=2)

    # Save results to flat CSV (flattened one-level only)
    flat_rows = []
    for section, content in results.items():
        if isinstance(content, dict):
            for subkey, subvalue in content.items():
                if isinstance(subvalue, dict):
                    for subsubkey, val in subvalue.items():
                        flat_rows.append({"Metric": f"{section} - {subkey} - {subsubkey}", "Value": val})
                else:
                    flat_rows.append({"Metric": f"{section} - {subkey}", "Value": subvalue})
        else:
            flat_rows.append({"Metric": section, "Value": content})

    pd.DataFrame(flat_rows).to_csv("evaluation_results.csv", index=False)
