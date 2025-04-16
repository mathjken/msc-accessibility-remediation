import json
import csv
import os

def extract_specific_wcag_violations(json_file_path):
    """
    Extracts accessibility violations related to WCAG 4.1.2 and 1.3.1 from an axe-core JSON output file
    nested under the 'accessibility' key.
    """
    violations_of_interest = []
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Navigate to the nested 'violations' key
        violations = data.get("accessibility", {}).get("violations", [])
        if not violations:
            print(f"⚠️ No 'violations' found under ['accessibility'] in {json_file_path}")
            return []

        for violation in violations:
            if any(tag in violation.get('tags', []) for tag in ['wcag412', 'wcag131']):
                violations_of_interest.append(violation)

    except FileNotFoundError:
        print(f"❌ File not found at {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in {json_file_path}")
        return []
    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {e}")
        return []

    return violations_of_interest


def export_violations_to_csv(violations, csv_file_path):
    """
    Exports the extracted violations to a CSV file.

    Args:
        violations (list): A list of dictionaries representing violations.
        csv_file_path (str): The path to the CSV file to be created.
    """
    if not violations:
        print("No violations to export to CSV.")
        return

    # Collect all unique keys from the violations for the CSV header
    headers = set()
    for violation in violations:
        headers.update(violation.keys())
    headers = sorted(list(headers))

    try:
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for violation in violations:
                writer.writerow(violation)
        print(f"✅ Successfully exported violations to {csv_file_path}")
    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")


def main():
    json_file_path = "5pillarsuk.com.json"

    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return
    else:
        print(f"✅ Found file: {json_file_path}")

    csv_file_path = "violations.csv"
    extracted_violations = extract_specific_wcag_violations(json_file_path)

    if extracted_violations:
        print(f"🔍 Found {len(extracted_violations)} WCAG 4.1.2 and 1.3.1 violations. Exporting to CSV...")
        export_violations_to_csv(extracted_violations, csv_file_path)
    else:
        print("ℹ️ No WCAG 4.1.2 or 1.3.1 violations found, or error occurred.")


if __name__ == "__main__":
    main()
