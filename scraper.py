import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import time

# -----------------------------
# Configuration
# -----------------------------

DIRECTORY_URL = "https://www.datarequests.org/company/"
JSON_BASE_URL = "https://www.datarequests.org/db/"

HEADERS = {
    "User-Agent": "PrivittyInternLeadResearchBot/1.0"
}

OUTPUT_FOLDER = "data"
CSV_FILE = os.path.join(OUTPUT_FOLDER, "raw_companies.csv")
JSON_FILE = os.path.join(OUTPUT_FOLDER, "raw_companies.json")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------
# Fetch directory page
# -----------------------------

print("=" * 60)
print("Fetching company directory...")
print("=" * 60)

response = requests.get(DIRECTORY_URL, headers=HEADERS, timeout=20)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a", href=True)

company_links = []

for link in links:

    href = link["href"]

    if href.startswith("https://www.datarequests.org/company/"):

        if href not in company_links:

            company_links.append(href)

TOTAL = len(company_links)

print(f"\nTotal company pages found: {TOTAL}\n")

# -----------------------------
# Scrape every company
# -----------------------------

companies = []

for index, company_url in enumerate(company_links, start=1):

    slug = company_url.rstrip("/").split("/")[-1]

    json_url = f"{JSON_BASE_URL}{slug}.json"

    percentage = (index / TOTAL) * 100

    print(f"[{index}/{TOTAL}] {percentage:.1f}%  ->  {slug}")

    try:

        response = requests.get(
            json_url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code == 200:

            company = response.json()

            companies.append({

                "Name": company.get("name"),

                "Slug": slug,

                "Email": company.get("email"),

                "Phone": company.get("phone"),

                "Website": company.get("web"),

                "Address": company.get("address"),

                "Categories": ", ".join(
                    company.get("categories", [])
                ),

                "Relevant Countries": ", ".join(
                    company.get("relevant-countries", [])
                ),

                "Quality": company.get("quality"),

                "Sources": ", ".join(
                    company.get("sources", [])
                ),

                "Directory URL": company_url,

                "JSON URL": json_url

            })

        else:

            print(f"JSON not found for {slug}")

    except Exception as e:

        print(f"Error processing {slug}: {e}")

    # -------------------------
    # Save progress every 100 companies
    # -------------------------

    if index % 100 == 0:

        df = pd.DataFrame(companies)

        df.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        with open(JSON_FILE, "w", encoding="utf-8") as f:

            json.dump(
                companies,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"\n✓ Progress saved ({index}/{TOTAL})\n")

    # Respect the server
    time.sleep(0.2)

# -----------------------------
# Final Save
# -----------------------------

df = pd.DataFrame(companies)

df.to_csv(
    CSV_FILE,
    index=False,
    encoding="utf-8-sig"
)

with open(JSON_FILE, "w", encoding="utf-8") as f:

    json.dump(
        companies,
        f,
        indent=4,
        ensure_ascii=False
    )

# -----------------------------
# Finished
# -----------------------------

print("\n" + "=" * 60)
print("SCRAPING COMPLETED SUCCESSFULLY")
print("=" * 60)

print(f"Companies Collected : {len(companies)}")
print(f"CSV Saved           : {CSV_FILE}")
print(f"JSON Saved          : {JSON_FILE}")