import json
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.compose import ColumnTransformer
import os
import re

# === Load JSON Data ===
input_file = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\EXPERIMENT\data\refiltered_violations_131_412.json"
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# === Flatten JSON into DataFrame ===
all_rows = []
for sc, violations in data.items():
    for v in violations:
        html = v.get("html", "")
        tag_match = re.search(r"<(\w+)", html)
        tag = tag_match.group(1) if tag_match else ""
        all_rows.append({
            "WCAG_SC": sc,
            "rule_id": v.get("rule_id"),
            "impact": v.get("impact"),
            "html": html,
            "tag": tag,
            "file": v.get("file", "")
        })

df = pd.DataFrame(all_rows)
df.fillna("", inplace=True)

# === Map Impact to Score ===
df["impact_score"] = df["impact"].map({
    "minor": 1, "moderate": 2, "serious": 3, "critical": 4
}).fillna(0)

# === Feature Encoding ===
categorical_features = ["WCAG_SC", "rule_id", "tag"]
numerical_features = ["impact_score"]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ("num", StandardScaler(), numerical_features)
])

X = preprocessor.fit_transform(df)

# === KMeans Clustering ===
kmeans = KMeans(n_clusters=2, random_state=42, n_init="auto")
df["kmeans_cluster"] = kmeans.fit_predict(X)

# === DBSCAN Clustering ===
dbscan = DBSCAN(eps=0.63, min_samples=5)
df["dbscan_cluster"] = dbscan.fit_predict(X)

# === Sample ~10 rows per cluster ===
sampled_kmeans = df.groupby("kmeans_cluster", group_keys=False).apply(lambda g: g.sample(min(len(g), 10), random_state=42)).reset_index(drop=True)
sampled_dbscan = df[df["dbscan_cluster"] != -1].groupby("dbscan_cluster", group_keys=False).apply(lambda g: g.sample(min(len(g), 10), random_state=42)).reset_index(drop=True)
# After sampling per cluster
sampled_dbscan = sampled_dbscan.sample(n=min(len(sampled_dbscan), 100), random_state=42)


# === Merge and Save ===
sampled_df = pd.concat([sampled_kmeans, sampled_dbscan], ignore_index=True).drop_duplicates()

sampled_df.to_json("clustered_violations.json", orient="records", indent=2)
sampled_df.to_csv("clustered_violations.csv", index=False)

print("✅ Clustering complete and reduced to manageable size.")
print(f"Sampled KMeans clusters: {sampled_kmeans['kmeans_cluster'].nunique()} (total: {len(sampled_kmeans)})")
print(f"Sampled DBSCAN clusters: {sampled_dbscan['dbscan_cluster'].nunique()} (total: {len(sampled_dbscan)})")
print(f"Total unique rows in final output: {len(sampled_df)}")
print("→ clustered_violations.json")
print("→ clustered_violations.csv")
