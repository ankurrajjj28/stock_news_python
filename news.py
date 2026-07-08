import requests
import pandas as pd
import ollama
import json

print("All libraries imported successfully.")

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.nseindia.com/"
})

# Cookie lena
session.get("https://www.nseindia.com")

# Latest announcements
url = "https://www.nseindia.com/api/corporate-announcements?index=equities"

response = session.get(url)

data = response.json()

df = pd.DataFrame(data)

print("Total Announcements :", len(df))

df[[
    "symbol",
    "sm_name",
    "desc",
    "an_dt"
]].head(10)

def analyze(company, category, announcement):

    prompt = f"""
You are a professional Indian Stock Market Analyst.

Analyze this NSE announcement.

Ignore these:
- Newspaper Publication
- Postal Ballot
- Scrutinizer Report
- AGM Notice
- Compliance Filing

Importance Guide:
10 = Very High
8 = High
5 = Medium
2 = Low

Return ONLY valid JSON.

{{
    "ignore": false,
    "summary": "",
    "impact": "",
    "importance": 0
}}

Company:
{company}

Category:
{category}

Announcement:
{announcement}
"""

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return json.loads(response["message"]["content"])

print("AI Function Ready")

def analyze(company, category, announcement):

    prompt = f"""
You are an Indian Stock Market Analyst.

Analyze this NSE announcement.

Ignore routine filings like:
- Newspaper Publication
- Postal Ballot
- Scrutinizer Report
- AGM
- Compliance Certificate
- Shareholding Pattern
- Closure of Trading Window
- Record Date
- Loss of Share Certificate

Return ONLY valid JSON.

{{
    "ignore": false,
    "summary": "",
    "importance": 0
}}

Importance Guide:

10 = Bankruptcy, Fraud, Insolvency, Large Acquisition, Major Order, Merger
9 = Order Win, Government Contract, Results, Buyback
8 = Dividend, Bonus, Split, Fund Raising, Rights Issue
7 = Joint Venture, New Plant, Expansion, Strategic Partnership
5 = General Business Update
1 = Routine Filing

Company:
{company}

Category:
{category}

Announcement:
{announcement}
"""

    response = ollama.chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response["message"]["content"])

import time

shown = set()

while True:

    print("\nChecking NSE...\n")

    session.get("https://www.nseindia.com")

    data = session.get(
        "https://www.nseindia.com/api/corporate-announcements?index=equities"
    ).json()

    df = pd.DataFrame(data)

    for i in range(len(df)):

        company = df.iloc[i]["sm_name"]
        category = str(df.iloc[i]["desc"])
        announcement = str(df.iloc[i]["attchmntText"])

        uid = company + announcement

        if uid in shown:
            continue
       # Fast keyword filter
        keywords = [
            "order", "contract", "acquisition", "merger",
            "results", "dividend", "bonus", "split",
            "buyback", "rights", "fund", "expansion",
            "joint venture", "approval", "investment",
            "government", "resignation", "ceo", "director",
            "fraud", "insolvency", "bankruptcy"
        ]

        text = (category + " " + announcement).lower()

        if not any(keyword in text for keyword in keywords):
            continue

        try:

            result = analyze(company, category, announcement)

            if result["ignore"]:
                continue

            score = int(result["importance"])

            if score < 7:
                continue

            shown.add(uid)

            emoji = "🟢" * min(score - 4, 5)
           print("=" * 90)
            print(f"{emoji}  {company}")
            print(f"⭐ Score : {score}/10\n")
            print(result["summary"])

        except Exception:
            pass

    print("\nNext scan in 30 seconds...\n")

    time.sleep(30)
