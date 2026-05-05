import sys, json
from datetime import datetime, timezone, timedelta

d = json.loads(sys.stdin.read())
bj_tz = timezone(timedelta(hours=8))
now = datetime.now(bj_tz).timestamp()

target_leagues = ['international', 'dreamleague', 'dream']
found = []
for m in d:
    league = (m.get('league_name') or '').lower()
    if any(t in league for t in target_leagues):
        st = m.get('start_time', 0)
        bj_time = datetime.fromtimestamp(st, tz=bj_tz).strftime('%Y-%m-%d %H:%M')
        is_upcoming = st > now
        found.append((st, f"  {'[UPCOMING]' if is_upcoming else '[PAST]'} {bj_time} | {m.get('league_name')} | {m.get('radiant_name','?')} vs {m.get('dire_name','?')}"))

found.sort(key=lambda x: x[0], reverse=True)
for _, s in found[:15]:
    print(s)

if not found:
    print('No TI/DreamLeague matches found')
    leagues = sorted(set(m.get('league_name','?') for m in d))
    print(f'Available leagues ({len(leagues)}):')
    for l in leagues:
        print(f'  {l}')
