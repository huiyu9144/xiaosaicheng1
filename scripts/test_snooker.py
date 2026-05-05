import subprocess, re

cmd = ["curl", "-s", "--compressed", "--max-time", "15", "https://www.snooker.org/res/index.asp?template=24"]
result = subprocess.run(cmd, capture_output=True, timeout=20)
html = result.stdout.decode("iso-8859-1")

print(f"HTML length: {len(html)}")
print(f"Has Upcoming Matches: {'Upcoming Matches' in html}")

rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
print(f"Total rows: {len(rows)}")

for i, row in enumerate(rows):
    if 'class="header"' in row.lower():
        print(f"Row {i}: HEADER")
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})Z', row)
    est_match = re.search(r'Est\.\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})Z', row)
    if date_match or est_match:
        clean = re.sub(r'<[^>]+>', ' ', row)
        clean = re.sub(r'&nbsp;', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f"Row {i}: {clean[:200]}")
