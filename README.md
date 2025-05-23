# 📘 MSc Accessibility Remediation using LLMs (GPT-4 + Axe-Core)

This repository supports a research project focused on evaluating and comparing two Large Language Model (LLM) prompting strategies—**Chain-of-Thought (CoT)** and **Retrieval-Augmented Generation (RAG)**—for automatically remediating **ARIA-related accessibility violations** in HTML code.

The approach uses **axe-core scan reports**, **WCAG-ACT test cases**, and **GPT-4**, with a methodology grounded in WCAG 2.2 Success Criteria.

---

## 📁 Project Structure

```
📦 msc-accessibility-remediation
├── 📂 data/                                # Folder containing 1000 axe-core JSON scan reports and sampling outputs
│   ├── filtered_violations_131_412_critical.json
│   ├── violation_summary.json
│   ├── violations_urls_critical.csv
│   ├── sampled_kmeans_violations.json / .csv
│   └── sampled_dbscan_violations.json / .csv
├── 📂 logs/                                # Weekly reflective journals
│   └── week_ending_2025_04_13.md
├── 📂 evaluation/                          # Evaluation scripts and outputs
│   ├── run_evaluation.py                  # Script to analyze Axe results and manual scores
│   ├── evaluation_results.csv             # Combined performance metrics (CoT vs RAG)
│   └── plots/                             # Folder for generated plots (bar charts, boxplots)
├── .env                                   # API Key (not committed)
├── run_clustering_sampling.py             # 🔍 Filters & clusters critical violations using KMeans and DBSCAN
├── run_cot_fixes.py                       # 🧠 Applies Chain-of-Thought prompting
├── run_rag_fixes.py                       # 📚 Applies RAG prompting with WCAG context
├── run_combined_fixes.py                  # 🔁 Applies both CoT and RAG for comparison
├── manual_scores_template.csv             # 📄 CSV for manual evaluation (Likert + comments)
├── README.md
└── .gitignore
```

---

## 🧪 Study Design Overview

### Objective
To test whether GPT-4 can generate accessible HTML fixes that comply with WCAG, specifically:
- SC **4.1.2** – Name, Role, Value
- SC **1.3.1** – Info and Relationships

### Workflow Steps
1. **Parse 1000 axe-core JSON files**, filter for "critical" violations only.
2. **Feature Engineering:**
   - One-hot encode `rule_id`, `tag`
   - Flag `aria` presence
   - Map `impact_score`
3. **Clustering (K-Means, DBSCAN)** to sample representative violations.
4. Apply **GPT-4 using CoT and RAG** prompts to generate accessibility fixes.
5. **Run Axe-Core re-evaluation** on fixed snippets.
6. **Manual Evaluation** using Likert-scale for correctness, completeness.
7. **Statistical Analysis**:
   - Shapiro-Wilk normality check
   - Paired t-test / Wilcoxon Signed-Rank test
   - Cohen’s d for effect size

---

## ✅ Evaluation Criteria

### Automated Metrics:
- **Correctness:** Axe-Core confirms original issue is resolved (binary: 1 = fixed, 0 = not).
- **WCAG Compliance Delta:** Change in number of violations pre- and post-fix.
- **Completeness:** No new issues introduced; all initial issues resolved.

### Manual Metrics (via `manual_scores_template.csv`):
- **Correctness** (1–5)
- **Completeness** (1–5)
- **Clarity / Readability** (1–5)
- **Fix Appropriateness** (1–5)
- **Comments**

### Charts & Reports
- 📊 **Bar charts**: Fix rates across CoT vs RAG
- 📉 **Boxplots**: Distribution of manual scores
- 📈 **Line/Delta plots**: Change in WCAG violations

---

## 🔍 Technologies Used

- 🧠 **OpenAI GPT-4** – Accessibility remediation via LLMs
- 📚 **LangChain** – Prompt orchestration (CoT and RAG)
- 🧪 **Axe-Core** – Pre/post accessibility scans
- 📊 **Scikit-learn, Pandas, Matplotlib** – Sampling, evaluation, plotting
- 🧪 **WCAG-ACT** – Pass/fail reference benchmarks

---

## 📆 Weekly Logs

- [Week Ending 13 April 2025](logs/week_ending_2025_04_13.md)

---

## 📄 License

This project is for academic research purposes and is shared under a research license. Contact the repository owner for collaboration or citation.