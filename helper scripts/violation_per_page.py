import pandas as pd

# === Input and Output Paths ===
input_csv = "wcag_critical_violations_allfiles.csv"
output_csv = "filtered_violation_summary.csv"

# === List of target files ===
target_files = [
    "jobs.gsk.com{en-gb{jobs{367909{lang=en-us&previousLocale=en-US.jsonld",
    "jobs.gsk.com{tr-tr{jobs{lang=tr-tr.jsonld",
    "www.landeskirche-hannovers.de{evlka-de{wir-fuer-sie{begleiten{seelsorge{flughafenseelsorge.jsonld",
    "ptxtherapy.com.jsonld",
    "www.prysmiangroup.com{en{markets{generation-transmission-and-distribution{hv-and-submarine-power-transmission.jsonld",
    "econ.jhu.edu{undergraduate{student-organizations.jsonld",
    "www.engineersireland.ie{Professionals{CPD-Careers{Career-development{Setting-up-as-a-contractor.jsonld",
    "www.landeskirche-hannovers.de{evlka-de{presse-und-medien{frontnews{2017{Weltausstellung-Reformation-.jsonld",
    "www.shoppurecam.com{purecam-gb-4g-lte-wireless-data-plan-24-per-month-3-month-commitment.jsonld",
    "www.avpgalaxy.net{avp-movies{avp-movie{theatrical-vs-unrated.jsonld",
    "hrs.isr.umich.edu{data-products{restricted-data.jsonld",
    "www.landeskirche-hannovers.de{evlka-de{wir-fuer-sie{kinder{kirche-und-kinder{kinder-glauben.jsonld",
    "www.actionforchildren.org.uk{about-us{our-people{leadership-team{mike-knight.jsonld",
    "migracion.gob.bo{index.php{node{260.jsonld",
    "raymond-hood-exhibition.brown.edu{2a.html.jsonld",
    "raymond-hood-exhibition.brown.edu.jsonld"
]

# === Load CSV ===
df = pd.read_csv(input_csv)

# === Filter for target files only (exact matches) ===
filtered_df = df[df["file"].isin(target_files)]

# === Group and sum violation counts ===
summary_df = filtered_df.groupby("file", as_index=False)["violation_count"].sum()
summary_df.rename(columns={"violation_count": "total_violations"}, inplace=True)

# === Save to CSV ===
summary_df.to_csv(output_csv, index=False)

print("✅ Filtered violation summary saved to:", output_csv)
