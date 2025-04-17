# evaluation_pipeline.py

import json
import os
import csv
from statistics import mean
from scipy.stats import shapiro, ttest_rel, wilcoxon
from sklearn.metrics import accuracy_score

# Load combined CoT & RAG fixes
with open("combined_cot_rag_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Load pre-saved Axe-Core results (must include rule_id & fixed status)
with open("axe_validation_results.json", "r", encoding="utf-8") as f:
    axe_results = json.load(f)

# Load manual scores (Likert-scale: 1-5)
with open("manual_scores.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    manual_scores = {row["id"]: row for row in reader}

# Evaluation containers
cot_scores = []
rag_scores = []
manual_cot = []
manual_rag = []

for entry in data:
    html_id = entry.get("id")
    rule = entry.get("rule_id")

    cot_fix = axe_results.get(html_id, {}).get("cot", {})
    rag_fix = axe_results.get(html_id, {}).get("rag", {})

    # Binary correctness from Axe-Core
    cot_scores.append(1 if cot_fix.get("rule_fixed") else 0)
    rag_scores.append(1 if rag_fix.get("rule_fixed") else 0)

    # Manual scoring (Likert scale)
    cot_score = int(manual_scores.get(html_id, {}).get("cot_score", 0))
    rag_score = int(manual_scores.get(html_id, {}).get("rag_score", 0))
    manual_cot.append(cot_score)
    manual_rag.append(rag_score)

# === STATS SECTION ===

# Normality Test
print("\n📊 Shapiro-Wilk Normality Test:")
print("CoT Manual Scores:", shapiro(manual_cot))
print("RAG Manual Scores:", shapiro(manual_rag))

# Paired t-test
print("\n📈 Paired t-test (Manual Scores):")
print(ttest_rel(manual_cot, manual_rag))

# Wilcoxon Signed-Rank Test
print("\n📉 Wilcoxon Test (Manual Scores):")
print(wilcoxon(manual_cot, manual_rag))

# Accuracy / correctness rates
print("\n✅ Fix Accuracy via Axe-Core:")
print("CoT Accuracy:", mean(cot_scores))
print("RAG Accuracy:", mean(rag_scores))

# Cohen's d
def cohens_d(x, y):
    diff = [a - b for a, b in zip(x, y)]
    return mean(diff) / (sum([(i - mean(diff))**2 for i in diff]) / len(diff))**0.5

print("\n📏 Effect Size (Cohen's d):")
print(cohens_d(manual_rag, manual_cot))
