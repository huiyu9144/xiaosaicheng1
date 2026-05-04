#!/usr/bin/env python3
"""
小赛程 - 自动赛程数据更新脚本
每天通过 ESPN API 拉取 NBA + 足球赛程，合并电竞/其他硬编码数据，生成 matches.json
"""

import json
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"

LEAGUES = [
    ("basketball", "nba", "NBA", "篮球"),
    ("soccer", "eng.1", "英超", "足球"),
    ("soccer", "esp.1", "西甲", "足球"),
    ("soccer", "ita.1", "意甲", "足球"),
    ("soccer", "ger.1", "德甲", "足球"),
    ("soccer", "uefa.champions", "欧冠", "足球"),
]

BJ_TZ = timezone(timedelta(hours=8))

HARDCODED_MATCHES = [
    {
        "league": "VCT CN", "leagueType": "VCT CN", "matchStage": "败者组1/4决赛",
        "leagueRound": None, "homeTeam": "JDG", "awayTeam": "DRG",
        "time": "17:00", "date": "2026-05-05", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "VCT CN", "leagueType": "VCT CN", "matchStage": "败者组1/4决赛",
        "leagueRound": None, "homeTeam": "AG", "awayTeam": "TYL",
        "time": "19:00", "date": "2026-05-05", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "VCT CN", "leagueType": "VCT CN", "matchStage": "胜者组决赛",
        "leagueRound": None, "homeTeam": "XLG", "awayTeam": "EDG",
        "time": "17:00", "date": "2026-05-08", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "VCT CN", "leagueType": "VCT CN", "matchStage": "败者组半决赛",
        "leagueRound": None, "homeTeam": "TBD", "awayTeam": "TBD",
        "time": "19:00", "date": "2026-05-08", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "VCT CN", "leagueType": "VCT CN", "matchStage": "败者组决赛",
        "leagueRound": None, "homeTeam": "TBD", "awayTeam": "TBD",
        "time": "17:00", "date": "2026-05-09", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "VCT CN", "leagueType": "VCT CN", "matchStage": "决赛",
        "leagueRound": None, "homeTeam": "TBD", "awayTeam": "TBD",
        "time": "17:00", "date": "2026-05-10", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "LCK", "leagueType": "LCK", "matchStage": "常规赛",
        "leagueRound": None, "homeTeam": "GEN", "awayTeam": "NS",
        "time": "16:00", "date": "2026-05-06", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "LCK", "leagueType": "LCK", "matchStage": "常规赛",
        "leagueRound": None, "homeTeam": "HLE", "awayTeam": "SOOP",
        "time": "18:00", "date": "2026-05-06", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "LPL", "leagueType": "LPL", "matchStage": "常规赛",
        "leagueRound": None, "homeTeam": "WE", "awayTeam": "iG",
        "time": "17:00", "date": "2026-05-06", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "LPL", "leagueType": "LPL", "matchStage": "常规赛",
        "leagueRound": None, "homeTeam": "TES", "awayTeam": "JDG",
        "time": "19:00", "date": "2026-05-06", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "PCL", "leagueType": "PCL", "matchStage": "小组赛",
        "leagueRound": None, "homeTeam": "S阶段", "awayTeam": "B组&C组",
        "time": "18:00", "date": "2026-05-05", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "PCL", "leagueType": "PCL", "matchStage": "小组赛",
        "leagueRound": None, "homeTeam": "S阶段", "awayTeam": "C组&A组",
        "time": "18:00", "date": "2026-05-06", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "PGS", "leagueType": "PGS", "matchStage": "小组赛",
        "leagueRound": None, "homeTeam": "PGS 4", "awayTeam": "小组赛",
        "time": "18:00", "date": "2026-05-20", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "DreamLeague", "leagueType": "TI", "matchStage": "小组赛",
        "leagueRound": None, "homeTeam": "S29", "awayTeam": "小组赛",
        "time": "18:00", "date": "2026-05-13", "category": "电竞", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "", "leagueType": "中超", "matchStage": "常规赛",
        "leagueRound": 10, "homeTeam": "青岛西海岸", "awayTeam": "天津津门虎",
        "time": "19:00", "date": "2026-05-05", "category": "足球", "isImportant": False, "status": "upcoming"
    },
    {
        "league": "", "leagueType": "中超", "matchStage": "常规赛",
        "leagueRound": 10, "homeTeam": "山东泰山", "awayTeam": "上海申花",
        "time": "19:35", "date": "2026-05-05", "category": "足球", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "", "leagueType": "中超", "matchStage": "常规赛",
        "leagueRound": 10, "homeTeam": "辽宁铁人", "awayTeam": "成都蓉城",
        "time": "19:35", "date": "2026-05-05", "category": "足球", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "", "leagueType": "中超", "matchStage": "常规赛",
        "leagueRound": 10, "homeTeam": "武汉三镇", "awayTeam": "青岛海牛",
        "time": "19:00", "date": "2026-05-06", "category": "足球", "isImportant": False, "status": "upcoming"
    },
    {
        "league": "", "leagueType": "中超", "matchStage": "常规赛",
        "leagueRound": 10, "homeTeam": "上海海港", "awayTeam": "深圳新鹏城",
        "time": "19:35", "date": "2026-05-06", "category": "足球", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "", "leagueType": "中超", "matchStage": "常规赛",
        "leagueRound": 10, "homeTeam": "北京国安", "awayTeam": "大连英博",
        "time": "19:35", "date": "2026-05-06", "category": "足球", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "世锦赛", "leagueType": "斯诺克", "matchStage": "决赛",
        "leagueRound": None, "homeTeam": "墨菲", "awayTeam": "吴宜泽",
        "time": "02:00", "date": "2026-05-05", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "世乒赛", "leagueType": "乒乓球", "matchStage": "32强",
        "leagueRound": None, "homeTeam": "中国", "awayTeam": "澳大利亚",
        "time": "17:00", "date": "2026-05-05", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "世乒赛", "leagueType": "乒乓球", "matchStage": "16强",
        "leagueRound": None, "homeTeam": "中国", "awayTeam": "TBD",
        "time": "17:00", "date": "2026-05-06", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "世乒赛", "leagueType": "乒乓球", "matchStage": "16强",
        "leagueRound": None, "homeTeam": "中国", "awayTeam": "TBD",
        "time": "17:00", "date": "2026-05-07", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "世乒赛", "leagueType": "乒乓球", "matchStage": "1/4决赛",
        "leagueRound": None, "homeTeam": "中国", "awayTeam": "TBD",
        "time": "17:00", "date": "2026-05-08", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "世乒赛", "leagueType": "乒乓球", "matchStage": "半决赛",
        "leagueRound": None, "homeTeam": "中国", "awayTeam": "TBD",
        "time": "17:00", "date": "2026-05-09", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "世乒赛", "leagueType": "乒乓球", "matchStage": "决赛",
        "leagueRound": None, "homeTeam": "中国", "awayTeam": "TBD",
        "time": "19:00", "date": "2026-05-10", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "泰国公开赛", "leagueType": "羽毛球", "matchStage": "32强",
        "leagueRound": None, "homeTeam": "石宇奇", "awayTeam": "陈雨菲",
        "time": "10:00", "date": "2026-05-12", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "马来西亚大师赛", "leagueType": "羽毛球", "matchStage": "32强",
        "leagueRound": None, "homeTeam": "李诗沣", "awayTeam": "王祉怡",
        "time": "10:00", "date": "2026-05-19", "category": "其他", "isImportant": True, "status": "upcoming"
    },
    {
        "league": "新加坡公开赛", "leagueType": "羽毛球", "matchStage": "32强",
        "leagueRound": None, "homeTeam": "何济霆", "awayTeam": "刘圣书",
        "time": "10:00", "date": "2026-05-26", "category": "其他", "isImportant": True, "status": "upcoming"
    },
]


def fetch_espn(sport, league):
    url = ESPN_SCOREBOARD.format(sport=sport, league=league)
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "xiaosaicheng/1.0"})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  [WARN] {sport}/{league} 拉取失败: {e}")
        return None


def utc_to_beijing(utc_str):
    dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    bj = dt.astimezone(BJ_TZ)
    return bj.strftime("%H:%M"), bj.strftime("%Y-%m-%d")


def parse_espn_events(data, league_type, category):
    matches = []
    if not data:
        return matches

    events = data.get("events", [])
    for event in events:
        for comp in event.get("competitions", []):
            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue

            home = competitors[0] if competitors[0].get("homeAway") == "home" else competitors[1]
            away = competitors[1] if competitors[0].get("homeAway") == "home" else competitors[0]

            home_name = home.get("team", {}).get("displayName", "?")
            away_name = away.get("team", {}).get("displayName", "?")

            utc_date = comp.get("date", "")
            if not utc_date:
                continue

            time_str, date_str = utc_to_beijing(utc_date)

            status_type = comp.get("status", {}).get("type", {})
            status_name = status_type.get("name", "")
            if status_name in ("STATUS_FINAL", "STATUS_FULL_TIME"):
                status = "finished"
            elif status_name in ("STATUS_IN_PROGRESS", "STATUS_FIRST_HALF", "STATUS_SECOND_HALF", "STATUS_HALFTIME"):
                status = "live"
            else:
                status = "upcoming"

            is_important = category == "篮球" or league_type in ("英超", "欧冠")

            matches.append({
                "league": "",
                "leagueType": league_type,
                "matchStage": "常规赛" if category == "足球" else "季后赛",
                "leagueRound": None,
                "homeTeam": home_name,
                "awayTeam": away_name,
                "time": time_str,
                "date": date_str,
                "category": category,
                "isImportant": is_important,
                "status": status,
            })

    return matches


def main():
    print("=" * 50)
    print(f"小赛程 数据更新 - {datetime.now(BJ_TZ).strftime('%Y-%m-%d %H:%M:%S')} BJT")
    print("=" * 50)

    all_matches = []

    for sport, league, league_type, category in LEAGUES:
        print(f"\n[拉取] {league_type} ({sport}/{league})")
        data = fetch_espn(sport, league)
        matches = parse_espn_events(data, league_type, category)
        print(f"  获取到 {len(matches)} 场比赛")
        all_matches.extend(matches)

    print(f"\n[合并] 硬编码数据 ({len(HARDCODED_MATCHES)} 场)")
    all_matches.extend(HARDCODED_MATCHES)

    today = datetime.now(BJ_TZ).strftime("%Y-%m-%d")
    all_matches = [m for m in all_matches if m["date"] >= today]

    category_order = {"电竞": 0, "篮球": 1, "足球": 2, "其他": 3}
    all_matches.sort(key=lambda m: (category_order.get(m["category"], 99), m["date"], m["time"]))

    output = {
        "version": 1,
        "updatedAt": datetime.now(BJ_TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "matches": all_matches,
    }

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] 共 {len(all_matches)} 场比赛写入 matches.json")
    cats = {}
    for m in all_matches:
        cats[m["category"]] = cats.get(m["category"], 0) + 1
    for cat, count in cats.items():
        print(f"  {cat}: {count} 场")


if __name__ == "__main__":
    main()
