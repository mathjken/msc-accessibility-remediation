import os
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN

# ✅ Define root path to the data folder
root_path = r"C:\Users\w23063958\OneDrive - Northumbria University - Production Azure AD\MSC PROJECT\1000study\data"
input_file = "filtered_violations_131_412_critical.json"
input_path = os.path.join(root_path, input_file)

# ✅ Load filtered critical WCAG violations
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# ✅ Merge both SC 1.3.1 and 4.1.2 violations
violations = data.get("1.3.1", []) + data.get("4.1.2", [])
df = pd.DataFrame(violations)

# ✅ Map impact to severity score
impact_map = {"minor": 1, "moderate": 2, "serious": 3, "critical": 4}
df["impact_score"] = df["impact"].map(impact_map).fillna(0)

# ✅ Extract HTML tag name
df["tag"] = df["html"].str.extract(r"<(\w+)", expand=False)

# ✅ Flag for ARIA-related rule_id
df["has_aria"] = df["rule_id"].apply(lambda x: 1 if "aria" in x.lower() else 0)

# ✅ One-hot encode categorical features
rule_ohe = pd.get_dummies(df["rule_id"], prefix="rule")
tag_ohe = pd.get_dummies(df["tag"], prefix="tag")

# ✅ Combine features
X = pd.concat([rule_ohe, tag_ohe, df[["impact_score", "has_aria"]]], axis=1)
X_scaled = StandardScaler().fit_transform(X)

# ✅ Apply KMeans
kmeans = KMeans(n_clusters=10, random_state=42)
df["kmeans_cluster"] = kmeans.fit_predict(X_scaled)

# ✅ Apply DBSCAN
dbscan = DBSCAN(eps=0.9, min_samples=5)
df["dbscan_cluster"] = dbscan.fit_predict(X_scaled)

# ✅ Sample one from each cluster
sample_kmeans = df.groupby("kmeans_cluster", group_keys=False).apply(lambda g: g.sample(1, random_state=42)).reset_index(drop=True)
sample_dbscan = df[df["dbscan_cluster"] != -1].groupby("dbscan_cluster", group_keys=False).apply(lambda g: g.sample(1)).reset_index(drop=True)

# ✅ Clean JSON/dict fields for CSV export
for col in ["tags", "nodes", "target", "html"]:
    for sample in [sample_kmeans, sample_dbscan]:
        if col in sample.columns:
            sample[col] = sample[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)

# ✅ Save outputs
sample_kmeans.to_json(os.path.join(root_path, "sampled_kmeans_violations.json"), orient="records", indent=2)
sample_dbscan.to_json(os.path.join(root_path, "sampled_dbscan_violations.json"), orient="records", indent=2)
sample_kmeans.to_csv(os.path.join(root_path, "sampled_kmeans_violations.csv"), index=False)
sample_dbscan.to_csv(os.path.join(root_path, "sampled_dbscan_violations.csv"), index=False)

# ✅ Preview tables
selected_fields = ["file", "rule_id", "impact", "tag", "html", "target"]

print("\n🧾 Sampled KMeans Violations:")
print(sample_kmeans[selected_fields + ["kmeans_cluster"]].to_string(index=False))
print("\nTotal sampled KMeans violations:", len(sample_kmeans))

print("\n🧾 Sampled DBSCAN Violations:")
print(sample_dbscan[selected_fields + ["dbscan_cluster"]].to_string(index=False))
print("\nTotal sampled DBSCAN violations:", len(sample_dbscan))

# ✅ Done
print("\n✅ Sampling complete. Files saved in:")
print(f" - {root_path}\\sampled_kmeans_violations.json / .csv")
print(f" - {root_path}\\sampled_dbscan_violations.json / .csv")