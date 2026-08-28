import pandas as pd

INPUT_FILE = "data/raw_companies.csv"
OUTPUT_FILE = "data/shortlisted_companies.csv"

# --------------------------------------------------
# Keywords important for Privitty
# --------------------------------------------------

HIGH_PRIORITY = [
    "finance",
    "bank",
    "banking",
    "insurance",
    "health",
    "healthcare",
    "medical",
    "hospital",
    "telecom",
    "telecommunication",
    "cloud",
    "saas",
    "security",
    "identity",
    "government"
]

MEDIUM_PRIORITY = [
    "advertising",
    "ads",
    "marketing",
    "social media",
    "retail",
    "ecommerce",
    "marketplace",
    "education"
]


def calculate_score(row):

    score = 0
    reasons = []

    categories = str(row.get("Categories", "")).lower()

    # High priority categories
    for word in HIGH_PRIORITY:
        if word in categories:
            score += 10
            reasons.append(word)
            break

    # Medium priority categories
    for word in MEDIUM_PRIORITY:
        if word in categories:
            score += 5
            reasons.append(word)
            break

    # Verified company
    if str(row.get("Quality", "")).lower() == "verified":
        score += 3
        reasons.append("verified")

    # Contact information
    if pd.notna(row.get("Email")) and str(row["Email"]).strip():
        score += 2
        reasons.append("email")

    if pd.notna(row.get("Phone")) and str(row["Phone"]).strip():
        score += 2
        reasons.append("phone")

    if pd.notna(row.get("Website")) and str(row["Website"]).strip():
        score += 2
        reasons.append("website")

    # Global company
    countries = str(row.get("Relevant Countries", "")).lower()

    if "all" in countries:
        score += 2
        reasons.append("global")

    return pd.Series([score, ", ".join(reasons)])


# --------------------------------------------------
# Load data
# --------------------------------------------------

print("Loading companies...")

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} companies")

# --------------------------------------------------
# Score
# --------------------------------------------------

df[["Lead Score", "Reason"]] = df.apply(
    calculate_score,
    axis=1
)

# --------------------------------------------------
# Sort
# --------------------------------------------------

df = df.sort_values(
    by="Lead Score",
    ascending=False
)

# --------------------------------------------------
# Keep ONLY Top 300
# --------------------------------------------------

TOP_N = 300

shortlisted = df.head(TOP_N).copy()

# Priority labels

def priority(score):

    if score >= 15:
        return "High"

    elif score >= 10:
        return "Medium"

    return "Low"

shortlisted["Priority"] = shortlisted["Lead Score"].apply(priority)

# --------------------------------------------------
# Save
# --------------------------------------------------

shortlisted.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\n==============================")
print("SCORING COMPLETE")
print("==============================")

print(f"Original companies : {len(df)}")
print(f"Shortlisted        : {len(shortlisted)}")
print(f"Saved to           : {OUTPUT_FILE}")

print("\nTop 20 Companies\n")

print(
    shortlisted[
        [
            "Name",
            "Lead Score",
            "Priority",
            "Categories"
        ]
    ].head(20)
)