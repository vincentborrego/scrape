import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import os

ids = random.sample(range(1, 8735), 5)

def get_manga_data(manga_id):
    url = f"https://mangapill.com/manga/{manga_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Title from <title> tag
        raw_title = soup.title.string.strip() if soup.title else "No title"
        title_tag = raw_title[0:-17]

        # Try to find description (grab first paragraph with enough content)
        description = ""

        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 50:  # adjust this threshold if needed
                description = text
                description = description.replace("\n", " ").replace("\r", "").strip()
                break

        if not description:
            return None  # Skip if we can't find a meaningful description

        return {
            "id": manga_id,
            "title": title_tag,
            "description": description
        }
    except Exception as e:
        print(f"Error on ID {manga_id}: {e}")
        return None

# Output file
csv_file = "manga_data.csv"
existing_ids = set()

# Check for existing data to avoid duplicates
if os.path.exists(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_ids.add(int(row["id"]))

# Start scraping
with open(csv_file, "a", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "description"], quoting=csv.QUOTE_ALL)
    if os.stat(csv_file).st_size == 0:
        writer.writeheader()  # Write header only once
    
    for manga_id in ids:  # 1 to 8734
        if manga_id in existing_ids:
            continue

        data = get_manga_data(manga_id)
        if data:
            print(f"[{data['id']}] {data['title']}")
            writer.writerow(data)
        else:
            print(f"[{manga_id}] No data found or skipped.")
        
        time.sleep(random.uniform(0.7, 1.3))  # polite delay