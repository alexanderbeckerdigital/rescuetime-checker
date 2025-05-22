import requests
from datetime import datetime, timedelta
from tabulate import tabulate
import os
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()
API_KEY = os.getenv("RESCUETIME_API_KEY")

# Datum heute und vor 7 Tagen
end_date = datetime.today()
start_date = end_date - timedelta(days=7)

# RescueTime API URL für Aktivitäten (Websites, Programme)
url = (
    "https://www.rescuetime.com/anapi/data?"
    f"key={API_KEY}"
    f"&perspective=interval"
    f"&restrict_kind=activity"
    f"&resolution_time=day"
    f"&restrict_begin={start_date.strftime('%Y-%m-%d')}"
    f"&restrict_end={end_date.strftime('%Y-%m-%d')}"
    "&format=json"
)

r = requests.get(url)
data = r.json()

# Header rausfinden (ist ein Array, z.B. ["Date", "Time Spent (seconds)", ...])
headers = data["row_headers"]
rows = data["rows"]

from collections import defaultdict

daily = defaultdict(list)
for row in rows:
    date = row[0]
    activity = row[3]  # Aktivität/Domain
    seconds = row[1]
    daily[date].append((activity, seconds))

for date in sorted(daily.keys()):
    print(f"\n{date} - Top 10 Aktivitäten/Websites:")
    top10 = sorted(daily[date], key=lambda x: x[1], reverse=True)[:10]
    table = [(act, round(sec / 3600, 2)) for act, sec in top10]
    print(tabulate(table, headers=["Domain/App", "Stunden"]))
