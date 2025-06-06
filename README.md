# 🔧 LLM-Based ARIA Accessibility Remediation Pipeline

This project explores the automated remediation of **ARIA-related accessibility violations** using **Large Language Models (LLMs)**. It evaluates two prompting strategies—**Chain-of-Thought (CoT)** and **Retrieval-Augmented Generation (RAG)**—to generate **WCAG 2.2-compliant** HTML fixes for violations under **Success Criteria SC 1.3.1** and **SC 4.1.2**.

---

## 📁 Dataset Structure

The dataset consists of accessibility scan outputs (Axe-Core `.jsonld` reports) for **1,000 URLs**, each with multiple HTML pages. These pages contain critical violations flagged under:

- `SC 1.3.1` – *Info & Relationships*
- `SC 4.1.2` – *Name, Role, Value*

---

## 🧪 Pipeline Overview

### 1. `extraction.py` – Extract Critical Violations

Parses `.jsonld` files to extract:
- Only **critical severity** violations
- That match **WCAG SC 1.3.1 and 4.1.2**

**Outputs:**
- `violations_urls_critical.csv`
- `violation_summary_critical.json`
- `filtered_violations_131_412_critical.json`

---

### 2. `sample_20percent.py` – Sample for LLM Evaluation

Randomly samples **20%** of the critical violations for evaluation.

**Input:**
- `violations_urls_critical.csv`

**Output:**
- `violations_urls_critical_sampled_20percent.csv`

---

### 3. `generate_prompts.py` – Prompt Construction for CoT & RAG

Builds LLM prompts for:
- **CoT (Chain-of-Thought)**
- **RAG (Retrieval-Augmented Generation)**

**Input:**
- `violations_urls_critical_sampled_20percent.csv`

**Output:**
- `prompts_cot_rag.csv`

---

### 4. `generate_fix.py` – Generate HTML Fixes via LLM

Uses GPT-4 (or compatible LLM) to generate accessibility fixes.

**Input:**
- `prompts_cot_rag.csv`

**Outputs:**
- `results_cot_rag_generated.csv`
- `results_cot_rag_generated.json`

---

### 5. `embed_fixes_into_html.py` – Integrate Fixes into HTML

Injects LLM-generated fixes into original HTML files with traceable wrappers.

**Input:**
- `results_cot_rag_generated.json`

**Output Directory:**
- `html_fixes_embedded/` — HTMLs ready for Axe-Core rescan.

---

### 6. `axecore_rerun.py` – Post-Fix Accessibility Re-Scanning

Reruns Axe-Core on the updated HTMLs.

**Input:**
- Files in `html_fixes_embedded/`

**Output:**
- `axe_json/` — Re-scanned reports for analysis

---

## 🧾 Evaluation Metrics

- **Fix Success Rate (%)**
- **Manual Completeness (Score = 2)**
- **Likert-Based Appropriateness Score (0–2 scale)**
- **WCAG Compliance Improvement (Axe-Core Delta)**
- **Statistical Tests:**
  - Shapiro-Wilk
  - Wilcoxon signed-rank
  - Independent t-test
  - One-way ANOVA

---

## 📊 Results Summary

| Metric                            | CoT        | RAG        |
|----------------------------------|------------|------------|
| ✅ Fix Success Rate (%)          | 93.75%     | 87.5%      |
| 🟢 Fully WCAG-Compliant Fixes    | 81.25%     | 56.25%     |
| 📉 Avg. Likert Score (Manual)    | 1.35       | 1.56       |
| 🚫 New Violations Introduced     | 0.0%       | 0.0%       |

---

## 🔍 Key Takeaways

- Fixes are applied at the **HTML node level**, not rule-level.
- All CoT and RAG prompts were grounded in WCAG techniques like:
  - `ARIA14`: Using `aria-label`
  - `G108`: Ensuring interactive elements are labeled
- Manual review confirms:
  - CoT is **more semantically accurate**
  - RAG is **more consistent but less complete**
- **LLMs can scale accessibility remediation** with prompt tuning.

---

## 📂 Directory Structure

```bash
📁 data/
├── violations_urls_critical.csv
├── violation_summary_critical.json
├── filtered_violations_131_412_critical.json
├── violations_urls_critical_sampled_20percent.csv
├── prompts_cot_rag.csv
├── results_cot_rag_generated.json
└── html_fixes_embedded/
