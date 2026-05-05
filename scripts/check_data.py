#!/usr/bin/env python3
import json
with open('matches.json') as f:
    data = json.load(f)

for cat in ['电竞', '篮球', '足球', '其他']:
    print(f'=== {cat} ===')
    for m in data['matches']:
        if m['category'] == cat:
            if cat in ('篮球', '足球'):
                print(f'  {m["date"]} {m["time"]} {m["leagueType"]:6s} {m["homeTeam"]:22s} vs {m["awayTeam"]:22s} [{m["status"]}]')
            else:
                print(f'  {m["date"]} {m["time"]} {m["leagueType"]:8s} {m["homeTeam"]:8s} vs {m["awayTeam"]:8s} [{m["matchStage"]}]')
    print()

print(f'Total: {len(data["matches"])} matches')
print(f'Updated: {data["updatedAt"]}')
