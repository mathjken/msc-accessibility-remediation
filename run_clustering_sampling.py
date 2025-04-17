
import json
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans, DBSCAN

# Load your filtered JSON
with open("filtered_violations_131_412.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Merge violations from both 1.3.1 and 4.1.2
violations = data["1.3.1"] + data["4.1.2"]
df = pd.DataFrame(violations)

# Impact severity encoding
impact_map = {"minor": 1, "moderate": 2, "serious": 3, "critical": 4}
df["impact_score"] = df["impact"].map(impact_map).fillna(0)

# HTML tag extraction
df["tag"] = df["html"].str.extract(r"<(\w+)", expand=False)

# ARIA presence flag
df["has_aria"] = df["rule_id"].apply(lambda x: 1 if "aria" in x.lower() else 0)

# One-hot encode rule_id and tag
rule_ohe = pd.get_dummies(df["rule_id"], prefix="rule")
tag_ohe = pd.get_dummies(df["tag"], prefix="tag")

# Feature matrix
X = pd.concat([rule_ohe, tag_ohe, df[["impact_score", "has_aria"]]], axis=1)
X_scaled = StandardScaler().fit_transform(X)

# K-Means Clustering
kmeans = KMeans(n_clusters=10, random_state=42)
df["kmeans_cluster"] = kmeans.fit_predict(X_scaled)

# DBSCAN Clustering
dbscan = DBSCAN(eps=0.9, min_samples=5)
df["dbscan_cluster"] = dbscan.fit_predict(X_scaled)

# Sampling strategy
sample_kmeans = df.groupby("kmeans_cluster").apply(lambda g: g.sample(1, random_state=42)).reset_index(drop=True)
sample_dbscan = df[df["dbscan_cluster"] != -1].groupby("dbscan_cluster").apply(lambda g: g.sample(1)).reset_index(drop=True)

# Save samples
sample_kmeans.to_json("sampled_kmeans_violations.json", orient="records", indent=2)
sample_dbscan.to_json("sampled_dbscan_violations.json", orient="records", indent=2)
sample_kmeans.to_csv("sampled_kmeans_violations.csv", index=False)
sample_dbscan.to_csv("sampled_dbscan_violations.csv", index=False)

print("✅ Sampling complete. Files saved:")
print(" - sampled_kmeans_violations.json / .csv")
print(" - sampled_dbscan_violations.json / .csv")
