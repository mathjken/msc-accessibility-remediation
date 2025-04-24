import os
import csv
import json
from selenium import webdriver
from axe_selenium_python import Axe
from tempfile import NamedTemporaryFile

# Setup output directory
output_dir = "axe_scan_reports"
os.makedirs(output_dir, exist_ok=True)
combined_results = []

# Setup headless browser
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load input CSV
with open("results_cot_rag_generated.csv", "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)

    for idx, row in enumerate(reader):
        for fix_type in ["cot", "rag"]:
            html_field = f"{fix_type}_response"  # use cot_response / rag_response
            html_content = row.get(html_field, "")
            if not html_content.strip():
                continue

            # Wrap in a basic HTML shell
            full_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head><meta charset="UTF-8"><title>Test {idx} {fix_type.upper()}</title></head>
            <body><main id="axe-scan-target">{html_content}</main></body>
            </html>
            """

            # Save to temporary file
            with NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp_file:
                tmp_file.write(full_html)
                temp_html_path = tmp_file.name

            # Open file in browser
            driver.get("file://" + os.path.abspath(temp_html_path))

            # Run Axe-Core scan
            axe = Axe(driver)
            axe.inject()
            results = axe.run("main#axe-scan-target")

            # Append context info
            results["source_index"] = idx
            results["source_id"] = row.get("id", f"row_{idx}")
            results["fix_type"] = fix_type

            # Save individual result (optional)
            individual_json = os.path.join(output_dir, f"axe_result_{fix_type}_{idx}.json")
            with open(individual_json, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

            # Collect for combined export
            for violation in results.get("violations", []):
                for node in violation.get("nodes", []):
                    combined_results.append({
                        "source_id": row.get("id", f"row_{idx}"),
                        "fix_type": fix_type,
                        "rule_id": violation.get("id"),
                        "description": violation.get("description"),
                        "impact": violation.get("impact"),
                        "html_snippet": node.get("html", ""),
                        "target_selector": ", ".join(node.get("target", [])),
                        "help_url": violation.get("helpUrl")
                    })

# Save combined results to CSV
combined_csv = os.path.join(output_dir, "axe_combined_scan_results.csv")
with open(combined_csv, "w", newline='', encoding="utf-8") as f:
    fieldnames = list(combined_results[0].keys())
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined_results)

print(f"✅ Axe-Core scans completed for all rows (CoT + RAG). CSV saved to: {combined_csv}")
driver.quit()
