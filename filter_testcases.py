import json
import openpyxl
from openpyxl.styles import Alignment

file_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIEMNT\testcases.json"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = f.read()
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()

data = json.loads(json_data)

count_all_1_3_1 = 0
count_html_1_3_1 = 0
count_all_4_1_2 = 0
count_html_4_1_2 = 0

for test_case in data.get("testcases", []):
    requirements = test_case.get("ruleAccessibilityRequirements")
    relative_path = test_case.get("relativePath", "")
    is_html = relative_path.lower().endswith(".html")

    if requirements is not None:
        if "wcag20:1.3.1" in requirements:
            count_all_1_3_1 += 1
            if is_html:
                count_html_1_3_1 += 1

        if "wcag20:4.1.2" in requirements:
            count_all_4_1_2 += 1
            if is_html:
                count_html_4_1_2 += 1

def calculate_percentage(part, total):
    if total > 0:
        return (part / total * 100)
    else:
        return None

# Create a new workbook
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "ACT Test Case Summary"

# Headers
headers = ["WCAG SC", "ACT Test Cases", "% HTML-Specific Test Cases"]
sheet.append(headers)

# Data
data_rows = [
    ["1.3.1", count_all_1_3_1, calculate_percentage(count_html_1_3_1, count_all_1_3_1)],
    ["4.1.2", count_all_4_1_2, calculate_percentage(count_html_4_1_2, count_all_4_1_2)],
]

for row in data_rows:
    sheet.append(row)

# Format the percentage column
for i, cell in enumerate(sheet["C"]):
    if i > 0 and cell.value is not None:  # Skip the header row
        cell.number_format = '0.00%'
        cell.alignment = Alignment(horizontal='center')

# Adjust column widths
for col in sheet.columns:
    max_length = 0
    column = col[0].column_letter  # Get the column name
    for cell in col:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except TypeError:
            pass
    adjusted_width = (max_length + 2)  # Add a little extra padding
    sheet.column_dimensions[column].width = adjusted_width

# Save the workbook
output_excel_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIEMNT\act_test_case_summary.xlsx"
workbook.save(output_excel_path)

print(f"\nTable exported to: {output_excel_path}")