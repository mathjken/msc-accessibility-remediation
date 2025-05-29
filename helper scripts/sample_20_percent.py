import pandas as pd
import random

# === Input & Output ===
input_csv = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data\violations_urls_critical.csv"
output_csv = input_csv.replace("critical.csv", "critical_sampled_20percent.csv")

# === Load full critical violation CSV ===
df = pd.read_csv(input_csv)
df.fillna("", inplace=True)

# === Optional: Filter only SC 1.3.1 and 4.1.2 ===
if "WCAG_SC" in df.columns:
    df = df[df["WCAG_SC"].isin(["1.3.1", "4.1.2"])]

# === Sample 20% of the data ===
sampled_df = df.sample(frac=0.2, random_state=42)

# === Save sampled CSV ===
sampled_df.to_csv(output_csv, index=False, encoding="utf-8")

# === Stats for original data ===
total_rows = len(df)
count_131 = df[df["WCAG_SC"] == "1.3.1"].shape[0]
count_412 = df[df["WCAG_SC"] == "4.1.2"].shape[0]
unique_files = df['file'].nunique() if 'file' in df.columns else "N/A"

# === Stats for sampled data ===
sampled_rows = len(sampled_df)
sampled_count_131 = sampled_df[sampled_df["WCAG_SC"] == "1.3.1"].shape[0]
sampled_count_412 = sampled_df[sampled_df["WCAG_SC"] == "4.1.2"].shape[0]

# === Generate Summary Report ===
summary = (
    f"After filtering and vectorizing accessibility data, the final dataset included "
    f"{total_rows:,} critical violations – {count_131:,} under WCAG SC 1.3.1 (Info and Relationships) "
    f"and {count_412:,} under SC 4.1.2 (Name, Role, Value) – from {unique_files:,} parsed HTML files.\n"
    f"A 20% sample containing {sampled_rows:,} rows has been saved: "
    f"{sampled_count_131:,} (SC 1.3.1), {sampled_count_412:,} (SC 4.1.2)."
)

# === Print and save summary ===
print("\n📄 Summary Report:\n")
print(summary)

summary_path = output_csv.replace(".csv", "_summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary)

print(f"\n📝 Summary saved to: {summary_path}")
print(f"✅ Sampled 20% saved to:\n{output_csv}")
print(f"📊 Original: {total_rows} rows → Sampled: {sampled_rows} rows")
