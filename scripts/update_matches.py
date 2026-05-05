#!/usr/bin/env python3
"""
小赛程 - 自动赛程数据更新脚本
数据源:
  - ESPN API: NBA, 英超, 西甲, 意甲, 德甲, 欧冠
  - Liquipedia API: VCT CN, LCK, LPL, PCL, PGS, DreamLeague
  - TheSportsDB API: 中超
  - snooker.org 抓取: 斯诺克
  - 硬编码: 乒乓球, 羽毛球
"""

import json
import re
import ssl
import gzip
import html
import time
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from io import BytesIO

ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
LIQUIPEDIA_API = "https://liquipedia.net/{wiki}/api.php?action=parse&page={page}&prop=text&format=json"
THESPORTSDB_API = "https://www.thesportsdb.com/api/v1/json/123"
SNOOKER_ORG_UPCOMING = "https://www.snooker.org/res/index.asp?template=24"

BJ_TZ = timezone(timedelta(hours=8))

ESPN_LEAGUES = [
    ("basketball", "nba", "NBA", "篮球"),
    ("soccer", "eng.1", "英超", "足球"),
    ("soccer", "esp.1", "西甲", "足球"),
    ("soccer", "ita.1", "意甲", "足球"),
    ("soccer", "ger.1", "德甲", "足球"),
    ("soccer", "uefa.champions", "欧冠", "足球"),
]

LIQUIPEDIA_SOURCES = [
    ("VCT CN", "valorant", "VCT/2026/China_League/Stage_1", "电竞", "VCT CN"),
    ("LCK", "leagueoflegends", "LCK/2026", "电竞", "LCK"),
    ("LPL", "leagueoflegends", "LPL/2026/Split_2", "电竞", "LPL"),
    ("PCL", "pubg", "PUBG_Champions_League/2026/Spring", "电竞", "PCL"),
    ("PGS", "pubg", "PUBG_Global_Series/2026/Circuit_2/Series_1", "电竞", "PGS"),
    ("DreamLeague", "dota2", "DreamLeague/29", "电竞", "DreamLeague"),
]

SKIP_TITLES = {
    "Korea Standard Time (UTC+9)", "China Standard Time (UTC+8)",
    "Japan Standard Time (UTC+9)", "Eastern Daylight Time (UTC-4)",
    "Pacific Daylight Time (UTC-7)", "Central European Summer Time (UTC+2)",
    "British Summer Time (UTC+1)", "Moscow Standard Time (UTC+3)",
    "Previous", "Next", "Show countdown",
}

SKIP_TITLE_PATTERNS = [
    r"^Match:ID",
    r"^Make match page",
    r"\(page does not exist\)$",
]

TEAM_NAME_MAP = {
    "Gen.G Esports": "GEN",
    "Hanwha Life Esports": "HLE",
    "Dplus Kia": "DK",
    "Dplus": "DK",
    "T1": "T1",
    "KT Rolster": "KT",
    "DN SOOPers": "SOOP",
    "SOOPers": "SOOP",
    "Nongshim RedForce": "NS",
    "BRION": "BRO",
    "Kiwoom DRX": "DRX",
    "FEARX": "BFX",
    "Bilibili Gaming": "BLG",
    "Top Esports": "TES",
    "JD Gaming": "JDG",
    "Anyone's Legend": "AL",
    "ThunderTalk Gaming": "TT",
    "LNG Esports": "LNG",
    "Team WE": "WE",
    "Invictus Gaming": "iG",
    "Weibo Gaming": "WBG",
    "Ultra Prime": "UP",
    "LGD Gaming": "LGD",
    "Oh My God": "OMG",
    "Royal Never Give Up": "RNG",
    "FunPlus Phoenix": "FPX",
    "Ninjas in Pyjamas": "NIP",
    "EDward Gaming": "EDG",
    "XLG Esports": "XLG",
    "Trace Esports": "TEC",
    "TYLOO": "TYL",
    "All Gamers": "AG",
    "Dragon Ranger Gaming": "DRG",
    "Titan Esports Club": "TEC",
    "Nova Esports": "NOVA",
    "Wolves Esports": "WOL",
}

SPORT_TEAM_CN = {
    # NBA
    "Atlanta Hawks": "亚特兰大老鹰",
    "Boston Celtics": "波士顿凯尔特人",
    "Brooklyn Nets": "布鲁克林篮网",
    "Charlotte Hornets": "夏洛特黄蜂",
    "Chicago Bulls": "芝加哥公牛",
    "Cleveland Cavaliers": "克利夫兰骑士",
    "Dallas Mavericks": "达拉斯独行侠",
    "Denver Nuggets": "丹佛掘金",
    "Detroit Pistons": "底特律活塞",
    "Golden State Warriors": "金州勇士",
    "Houston Rockets": "休斯顿火箭",
    "Indiana Pacers": "印第安纳步行者",
    "LA Clippers": "洛杉矶快船",
    "Los Angeles Lakers": "洛杉矶湖人",
    "Memphis Grizzlies": "孟菲斯灰熊",
    "Miami Heat": "迈阿密热火",
    "Milwaukee Bucks": "密尔沃基雄鹿",
    "Minnesota Timberwolves": "明尼苏达森林狼",
    "New Orleans Pelicans": "新奥尔良鹈鹕",
    "New York Knicks": "纽约尼克斯",
    "Oklahoma City Thunder": "俄克拉荷马雷霆",
    "Orlando Magic": "奥兰多魔术",
    "Philadelphia 76ers": "费城76人",
    "Phoenix Suns": "菲尼克斯太阳",
    "Portland Trail Blazers": "波特兰开拓者",
    "Sacramento Kings": "萨克拉门托国王",
    "San Antonio Spurs": "圣安东尼奥马刺",
    "Toronto Raptors": "多伦多猛龙",
    "Utah Jazz": "犹他爵士",
    "Washington Wizards": "华盛顿奇才",
    # 英超
    "Arsenal": "阿森纳",
    "Aston Villa": "阿斯顿维拉",
    "Bournemouth": "伯恩茅斯",
    "Brentford": "布伦特福德",
    "Brighton & Hove Albion": "布莱顿",
    "Brighton and Hove Albion": "布莱顿",
    "Chelsea": "切尔西",
    "Crystal Palace": "水晶宫",
    "Everton": "埃弗顿",
    "Fulham": "富勒姆",
    "Ipswich Town": "伊普斯维奇",
    "Leicester City": "莱斯特城",
    "Liverpool": "利物浦",
    "Manchester City": "曼城",
    "Manchester United": "曼联",
    "Newcastle United": "纽卡斯尔联",
    "Nottingham Forest": "诺丁汉森林",
    "Southampton": "南安普顿",
    "Tottenham Hotspur": "托特纳姆热刺",
    "West Ham United": "西汉姆联",
    "Wolverhampton Wanderers": "狼队",
    "Wolves": "狼队",
    # 西甲
    "Alavés": "阿拉维斯",
    "Deportivo Alavés": "阿拉维斯",
    "Athletic Club": "毕尔巴鄂竞技",
    "Athletic Bilbao": "毕尔巴鄂竞技",
    "Atlético Madrid": "马德里竞技",
    "Atletico Madrid": "马德里竞技",
    "Barcelona": "巴塞罗那",
    "Celta Vigo": "塞尔塔",
    "Celta de Vigo": "塞尔塔",
    "Espanyol": "西班牙人",
    "Getafe": "赫塔费",
    "Girona": "赫罗纳",
    "Las Palmas": "拉斯帕尔马斯",
    "Leganés": "莱加内斯",
    "Mallorca": "马略卡",
    "Osasuna": "奥萨苏纳",
    "Rayo Vallecano": "巴列卡诺",
    "Real Betis": "皇家贝蒂斯",
    "Real Madrid": "皇家马德里",
    "Real Sociedad": "皇家社会",
    "Sevilla": "塞维利亚",
    "Valencia": "瓦伦西亚",
    "Valladolid": "巴拉多利德",
    "Real Valladolid": "巴拉多利德",
    "Villarreal": "比利亚雷亚尔",
    # 意甲
    "AC Milan": "AC米兰",
    "Atalanta": "亚特兰大",
    "Bologna": "博洛尼亚",
    "Cagliari": "卡利亚里",
    "Como": "科莫",
    "Empoli": "恩波利",
    "Fiorentina": "佛罗伦萨",
    "Genoa": "热那亚",
    "Hellas Verona": "维罗纳",
    "Inter Milan": "国际米兰",
    "Internazionale": "国际米兰",
    "Juventus": "尤文图斯",
    "Lazio": "拉齐奥",
    "Lecce": "莱切",
    "Monza": "蒙扎",
    "Napoli": "那不勒斯",
    "Parma": "帕尔马",
    "AS Roma": "罗马",
    "Roma": "罗马",
    "Torino": "都灵",
    "Udinese": "乌迪内斯",
    "Venezia": "威尼斯",
    "Cremonese": "克雷莫纳",
    # 德甲
    "FC Augsburg": "奥格斯堡",
    "Augsburg": "奥格斯堡",
    "Bayer Leverkusen": "勒沃库森",
    "Bayer 04 Leverkusen": "勒沃库森",
    "Bayern Munich": "拜仁慕尼黑",
    "Bayern München": "拜仁慕尼黑",
    "FC Bayern München": "拜仁慕尼黑",
    "Borussia Dortmund": "多特蒙德",
    "Borussia Mönchengladbach": "门兴格拉德巴赫",
    "Borussia Monchengladbach": "门兴格拉德巴赫",
    "Eintracht Frankfurt": "法兰克福",
    "SC Freiburg": "弗赖堡",
    "Freiburg": "弗赖堡",
    "Heidenheim": "海登海姆",
    "1. FC Heidenheim": "海登海姆",
    "TSG Hoffenheim": "霍芬海姆",
    "Hoffenheim": "霍芬海姆",
    "Holstein Kiel": "基尔",
    "RB Leipzig": "莱比锡红牛",
    "Mainz": "美因茨",
    "1. FSV Mainz 05": "美因茨",
    "FC St. Pauli": "圣保利",
    "St. Pauli": "圣保利",
    "VfB Stuttgart": "斯图加特",
    "Stuttgart": "斯图加特",
    "Union Berlin": "柏林联合",
    "1. FC Union Berlin": "柏林联合",
    "Werder Bremen": "云达不莱梅",
    "SV Werder Bremen": "云达不莱梅",
    "VfL Wolfsburg": "沃尔夫斯堡",
    "Wolfsburg": "沃尔夫斯堡",
    "VfL Bochum": "波鸿",
    "Bochum": "波鸿",
    # 欧冠常见队（不在上面联赛中的）
    "Paris Saint-Germain": "巴黎圣日耳曼",
    "PSG": "巴黎圣日耳曼",
    "Benfica": "本菲卡",
    "SL Benfica": "本菲卡",
    "Porto": "波尔图",
    "FC Porto": "波尔图",
    "Sporting CP": "葡萄牙体育",
    "Sporting Lisbon": "葡萄牙体育",
    "Ajax": "阿贾克斯",
    "PSV Eindhoven": "埃因霍温",
    "Feyenoord": "费耶诺德",
    "Celtic": "凯尔特人",
    "Rangers": "格拉斯哥流浪者",
    "Shakhtar Donetsk": "顿涅茨克矿工",
    "RB Salzburg": "萨尔茨堡红牛",
    "FC Salzburg": "萨尔茨堡红牛",
    "Galatasaray": "加拉塔萨雷",
    "Fenerbahçe": "费内巴切",
    "Fenerbahce": "费内巴切",
    "Olympiacos": "奥林匹亚科斯",
    "Panathinaikos": "帕纳辛奈科斯",
    "Club Brugge": "布鲁日",
    "Anderlecht": "安德莱赫特",
    "AS Monaco": "摩纳哥",
    "Monaco": "摩纳哥",
    "Lille": "里尔",
    "LOSC Lille": "里尔",
    "Marseille": "马赛",
    "Olympique de Marseille": "马赛",
    "Lyon": "里昂",
    "Olympique Lyonnais": "里昂",
    "Stade Rennais": "雷恩",
    "Rennes": "雷恩",
    "Nice": "尼斯",
    "OGC Nice": "尼斯",
    "Lens": "朗斯",
    "RC Lens": "朗斯",
    "Stade Brestois": "布雷斯特",
    "Brest": "布雷斯特",
    "Dinamo Zagreb": "萨格勒布迪纳摩",
    "Young Boys": "伯尔尼年轻人",
    "Sparta Prague": "布拉格斯巴达",
    "Slavia Prague": "布拉格斯拉维亚",
    "FK Crvena zvezda": "贝尔格莱德红星",
    "Red Star Belgrade": "贝尔格莱德红星",
    "FC Midtjylland": "中日德兰",
    "FC København": "哥本哈根",
    "Copenhagen": "哥本哈根",
    "Bodø/Glimt": "博德闪耀",
    "Molde": "莫尔德",
    "Malmö FF": "马尔默",
    "Maccabi Haifa": "海法马卡比",
    "Maccabi Tel Aviv": "特拉维夫马卡比",
    "Qarabağ": "卡拉巴赫",
    "Ferencváros": "费伦茨瓦罗斯",
}

CSL_TEAM_CN = {
    "Chengdu Rongcheng": "成都蓉城",
    "Shenzhen Peng City": "深圳新鹏城",
    "Shandong Taishan": "山东泰山",
    "Liaoning Tieren": "辽宁铁人",
    "Tianjin Jinmen Tiger": "天津津门虎",
    "Chongqing Tonglianglong": "重庆铜梁龙",
    "Shanghai Shenhua": "上海申花",
    "Dalian Yingbo": "大连英博",
    "Shanghai Port": "上海海港",
    "Henan FC": "河南队",
    "Beijing Guoan": "北京国安",
    "Qingdao West Coast": "青岛西海岸",
    "Wuhan Three Towns": "武汉三镇",
    "Qingdao Hainiu": "青岛海牛",
    "Hangzhou Greentown": "浙江队",
    "Zhejiang": "浙江队",
    "Yunnan Yukun": "云南玉昆",
    "Meizhou Hakka": "梅州客家",
    "Changchun Yatai": "长春亚泰",
    "Nantong Zhiyun": "南通支云",
    "Cangzhou Mighty Lions": "沧州雄狮",
    "Guangzhou Evergrande": "广州队",
    "Guangzhou FC": "广州队",
}

HARDCODED_OTHER = [
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

HARDCODED_ESPORTS_FALLBACK = [
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
]

HARDCODED_CSL = [
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
]


def cycle_vpn():
    """切换 VPN 获取新 IP，绕过 Liquipedia 限流"""
    vpn_name = "ZodAccess VPN"
    try:
        subprocess.run(["scutil", "--nc", "stop", vpn_name],
                       capture_output=True, timeout=10)
        time.sleep(3)
        subprocess.run(["scutil", "--nc", "start", vpn_name],
                       capture_output=True, timeout=10)
        time.sleep(5)
        print(f"  [VPN] 已切换 IP")
        return True
    except Exception as e:
        print(f"  [VPN] 切换失败: {e}")
        return False


def try_unblock_liquipedia():
    """尝试通过 token/generate 解除 Liquipedia 限流"""
    try:
        cmd = ["curl", "-s", "--max-time", "10", "https://liquipedia.net/token/generate"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and "token/unblock?token=" in result.stdout:
            token_match = re.search(r'token/unblock\?token=(\S+)', result.stdout)
            if token_match:
                token = token_match.group(1)
                unblock_url = f"https://liquipedia.net/token/unblock?token={token}"
                cmd2 = ["curl", "-s", "--max-time", "10", unblock_url]
                result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=15)
                if "Rate Limited" not in result2.stdout:
                    print(f"  [UNBLOCK] IP 已解除限流")
                    return True
    except Exception:
        pass
    return False


def fetch_url(url, extra_headers=None, retry_on_limit=True):
    """通用 HTTP GET 请求，支持 gzip，urllib 失败时回退到 curl，限流时尝试解除"""
    headers = {"User-Agent": "xiaosaicheng/1.0", "Accept-Encoding": "gzip"}
    if extra_headers:
        headers.update(extra_headers)

    for attempt in range(3):
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                data = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                text = data.decode()
                if "Rate Limited" in text and retry_on_limit and attempt < 2:
                    print(f"  [限流] 尝试解除 (第{attempt+1}次)")
                    try_unblock_liquipedia()
                    time.sleep(10)
                    continue
                return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code == 429 and retry_on_limit and attempt < 2:
                print(f"  [限流 429] 尝试解除 (第{attempt+1}次)")
                try_unblock_liquipedia()
                time.sleep(10)
                continue
        except Exception:
            pass

        try:
            cmd = ["curl", "-s", "--compressed", "--max-time", "15"]
            for k, v in headers.items():
                cmd.extend(["-H", f"{k}: {v}"])
            cmd.append(url)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if result.returncode == 0 and result.stdout.strip():
                if "Rate Limited" in result.stdout and retry_on_limit and attempt < 2:
                    print(f"  [限流] 尝试解除 (第{attempt+1}次)")
                    try_unblock_liquipedia()
                    time.sleep(10)
                    continue
                return json.loads(result.stdout)
        except Exception:
            pass

        if attempt < 2:
            print(f"  [重试] 等待后重试 (第{attempt+1}次)")
            time.sleep(10)

    print(f"  [WARN] 请求失败: {url}")
    return None


def fetch_espn(sport, league):
    url = ESPN_SCOREBOARD.format(sport=sport, league=league)
    return fetch_url(url)


def fetch_liquipedia(wiki, page):
    url = LIQUIPEDIA_API.format(wiki=wiki, page=page)
    return fetch_url(url)


def utc_to_beijing(utc_str):
    dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    bj = dt.astimezone(BJ_TZ)
    return bj.strftime("%H:%M"), bj.strftime("%Y-%m-%d")


def timestamp_to_beijing(ts):
    """Unix 时间戳转北京时间"""
    dt = datetime.fromtimestamp(int(ts), tz=BJ_TZ)
    return dt.strftime("%H:%M"), dt.strftime("%Y-%m-%d")


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

            home_name = SPORT_TEAM_CN.get(home_name, home_name)
            away_name = SPORT_TEAM_CN.get(away_name, away_name)

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


def short_team_name(name):
    """将完整队名映射为短名，先解码HTML实体"""
    decoded = html.unescape(name)
    return TEAM_NAME_MAP.get(decoded, decoded)


def is_valid_team(title):
    """检查 title 是否为有效队伍名"""
    if title in SKIP_TITLES:
        return False
    if "Special:" in title or "Template:" in title or "File:" in title:
        return False
    for pat in SKIP_TITLE_PATTERNS:
        if re.search(pat, title):
            return False
    return True


def parse_liquipedia_carousel(text, league_type, category):
    """
    解析 Liquipedia 的 carousel 格式 (LCK, LPL, VCT)
    找到所有 carousel-item 中的 data-timestamp，提取队伍名和阶段
    """
    matches = []
    
    carousel_items = re.finditer(r'carousel-item[^>]*>', text)
    
    for ci_match in carousel_items:
        ci_start = ci_match.start()
        ci_end = min(len(text), ci_start + 3000)
        item_text = text[ci_start:ci_end]
        
        ts_match = re.search(r'data-timestamp="(\d+)"', item_text)
        if not ts_match:
            continue
        
        ts = ts_match.group(1)
        
        stage_match = re.search(r'match-info-stage">([^<]+)<', item_text)
        stage = stage_match.group(1).strip() if stage_match else "常规赛"
        
        team_titles = re.findall(r'title="([^"]+)"', item_text)
        real_teams = []
        for t in team_titles:
            if not is_valid_team(t):
                continue
            if t not in real_teams:
                real_teams.append(t)
        
        if len(real_teams) >= 2:
            time_str, date_str = timestamp_to_beijing(ts)
            matches.append({
                "league": "",
                "leagueType": league_type,
                "matchStage": stage,
                "leagueRound": None,
                "homeTeam": short_team_name(real_teams[0]),
                "awayTeam": short_team_name(real_teams[1]),
                "time": time_str,
                "date": date_str,
                "category": category,
                "isImportant": True,
                "status": "upcoming",
            })
    
    return matches


def parse_pubg_carousel(text, league_type, category):
    """
    解析 PUBG 的 carousel 格式（大逃杀模式）
    每个 carousel-item 是一局游戏（地图），按日期+阶段分组为一个比赛日
    """
    from collections import defaultdict
    
    days = defaultdict(lambda: {"stages": set(), "times": [], "map_count": 0})
    
    for ci_match in re.finditer(r'carousel-item[^>]*>', text):
        ci_start = ci_match.start()
        ci_end = min(len(text), ci_start + 3000)
        item_text = text[ci_start:ci_end]
        
        ts_match = re.search(r'data-timestamp="(\d+)"', item_text)
        if not ts_match:
            continue
        
        ts = ts_match.group(1)
        time_str, date_str = timestamp_to_beijing(ts)
        
        stage_match = re.search(r'match-info-stage">([^<]+)<', item_text)
        stage = stage_match.group(1).strip() if stage_match else ""
        
        if stage and stage != "Results":
            days[date_str]["stages"].add(stage)
        days[date_str]["times"].append(time_str)
        
        ffa_match = re.search(r'match-info-ffa-info">([^<]+)<', item_text)
        if ffa_match:
            days[date_str]["map_count"] += 1
    
    matches = []
    for date_str in sorted(days.keys()):
        info = days[date_str]
        stage_str = ", ".join(sorted(info["stages"])) if info["stages"] else "小组赛"
        time_str = min(info["times"]) if info["times"] else "18:00"
        map_count = info["map_count"]
        
        matches.append({
            "league": "",
            "leagueType": league_type,
            "matchStage": stage_str,
            "leagueRound": None,
            "homeTeam": f"{map_count}局比赛",
            "awayTeam": stage_str,
            "time": time_str,
            "date": date_str,
            "category": category,
            "isImportant": True,
            "status": "upcoming",
        })
    
    return matches


def parse_liquipedia_matches(text, league_type, category, wiki_name):
    """统一解析 Liquipedia 页面中的比赛数据，按 wiki 类型选择解析器"""
    if wiki_name in ("pubg",):
        if 'carousel-item' in text and 'data-timestamp' in text:
            return parse_pubg_carousel(text, league_type, category)
        return []
    
    if 'data-timestamp' in text:
        return parse_liquipedia_carousel(text, league_type, category)
    
    return []


def fetch_thesportsdb(endpoint):
    """从 TheSportsDB 免费 API 获取数据"""
    url = f"{THESPORTSDB_API}/{endpoint}"
    return fetch_url(url, retry_on_limit=False)


def fetch_snooker_org():
    """从 snooker.org 抓取即将到来的比赛"""
    try:
        cmd = ["curl", "-s", "--compressed", "--max-time", "15", SNOOKER_ORG_UPCOMING]
        result = subprocess.run(cmd, capture_output=True, timeout=20)
        if result.returncode == 0 and result.stdout:
            for encoding in ["utf-8", "iso-8859-1", "latin-1", "cp1252"]:
                try:
                    return result.stdout.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    continue
            return result.stdout.decode("utf-8", errors="replace")
    except Exception:
        pass
    return None


def parse_csl_events(data):
    """解析 TheSportsDB 中超数据"""
    matches = []
    if not data:
        return matches
    events = data.get("events", [])
    if not events:
        return matches

    for event in events:
        home_name = event.get("strHomeTeam", "")
        away_name = event.get("strAwayTeam", "")
        if not home_name or not away_name:
            continue

        home_name = CSL_TEAM_CN.get(home_name, home_name)
        away_name = CSL_TEAM_CN.get(away_name, away_name)

        date_str = event.get("dateEvent", "")
        time_str = event.get("strTime", "")
        if not date_str:
            continue

        if time_str:
            time_str = time_str[:5]

        str_timestamp = event.get("strTimestamp", "")
        if str_timestamp:
            try:
                utc_dt = datetime.strptime(str_timestamp, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                bj_dt = utc_dt.astimezone(BJ_TZ)
                date_str = bj_dt.strftime("%Y-%m-%d")
                time_str = bj_dt.strftime("%H:%M")
            except ValueError:
                pass

        round_num = event.get("intRound", "")
        try:
            round_num = int(round_num)
        except (ValueError, TypeError):
            round_num = None

        is_important = home_name in ("山东泰山", "上海申花", "北京国安", "上海海港", "成都蓉城") or \
                       away_name in ("山东泰山", "上海申花", "北京国安", "上海海港", "成都蓉城")

        matches.append({
            "league": "",
            "leagueType": "中超",
            "matchStage": "常规赛",
            "leagueRound": round_num,
            "homeTeam": home_name,
            "awayTeam": away_name,
            "time": time_str,
            "date": date_str,
            "category": "足球",
            "isImportant": is_important,
            "status": "upcoming",
        })

    return matches


def parse_snooker_org(html_text):
    """解析 snooker.org 的即将到来比赛页面"""
    matches = []
    if not html_text:
        return matches

    tournament_name = "斯诺克"
    title_match = re.search(r'<a class="title"[^>]*>([^<]+)</a>', html_text)
    if title_match:
        raw_name = title_match.group(1).strip()
        raw_name = raw_name.replace('&#8209;', '-').replace('&nbsp;', ' ')
        tournament_name = html.unescape(raw_name)

    row_pattern = re.compile(r'<tr\s+class="[^"]*oneonone[^"]*"[^>]*>(.*?)</tr>', re.DOTALL)
    rows = row_pattern.findall(html_text)

    for row in rows:
        scheduled_match = re.search(r'<span class="scheduled"[^>]*>(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})Z</span>', row)
        if not scheduled_match:
            continue

        utc_str = scheduled_match.group(1)
        try:
            utc_dt = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            bj_dt = utc_dt.astimezone(BJ_TZ)
            date_str = bj_dt.strftime("%Y-%m-%d")
            time_str = bj_dt.strftime("%H:%M")
        except ValueError:
            continue

        round_match = re.search(r'<td class="round"[^>]*>.*?<a[^>]*>([^<]+)</a>', row, re.DOTALL)
        stage = html.unescape(round_match.group(1).strip()) if round_match else ""

        player_matches = re.findall(r'<td class="player\s*"[^>]*>.*?<a[^>]*>([^<]+)</a>', row, re.DOTALL)
        if len(player_matches) < 2:
            continue

        home_team = player_matches[0].strip()
        away_team = player_matches[1].strip()

        if '/' in away_team:
            away_team = "TBD"

        matches.append({
            "league": tournament_name,
            "leagueType": "斯诺克",
            "matchStage": stage,
            "leagueRound": None,
            "homeTeam": home_team,
            "awayTeam": away_team,
            "time": time_str,
            "date": date_str,
            "category": "其他",
            "isImportant": "Final" in stage or "Semi" in stage,
            "status": "upcoming",
        })

    return matches


def main():
    print("=" * 60)
    print(f"小赛程 数据更新 - {datetime.now(BJ_TZ).strftime('%Y-%m-%d %H:%M:%S')} BJT")
    print("=" * 60)

    all_matches = []
    liquipedia_success = set()

    # 1. ESPN API - 篮球和足球
    print("\n[数据源] ESPN API")
    print("-" * 40)
    for sport, league, league_type, category in ESPN_LEAGUES:
        print(f"  [拉取] {league_type} ({sport}/{league})")
        data = fetch_espn(sport, league)
        matches = parse_espn_events(data, league_type, category)
        print(f"    -> {len(matches)} 场比赛")
        all_matches.extend(matches)

    # 2. Liquipedia API - 电竞
    print("\n[数据源] Liquipedia API")
    print("-" * 40)
    for i, (league_type, wiki, page, category, key) in enumerate(LIQUIPEDIA_SOURCES):
        if i > 0:
            print(f"  [等待] 延迟 15 秒避免限流...")
            time.sleep(15)
        print(f"  [拉取] {league_type} ({wiki}/{page})")
        data = fetch_liquipedia(wiki, page)
        if data:
            text = data.get("parse", {}).get("text", {}).get("*", "")
            if text:
                matches = parse_liquipedia_matches(text, league_type, category, wiki)
                if matches:
                    print(f"    -> {len(matches)} 场比赛 (来自Liquipedia)")
                    all_matches.extend(matches)
                    liquipedia_success.add(key)
                else:
                    print(f"    -> 解析到 0 场比赛，将使用硬编码数据")
            else:
                print(f"    -> 页面无内容，将使用硬编码数据")
        else:
            print(f"    -> API请求失败，将使用硬编码数据")

    # 3. TheSportsDB API - 中超
    print("\n[数据源] TheSportsDB API - 中超")
    print("-" * 40)
    csl_data = fetch_thesportsdb("eventsnextleague.php?id=4359")
    csl_matches = parse_csl_events(csl_data)
    print(f"  [拉取] 中超 -> {len(csl_matches)} 场比赛")
    if csl_matches:
        all_matches.extend(csl_matches)
    print(f"  [补充] 中超硬编码 ({len(HARDCODED_CSL)} 场)")
    all_matches.extend(HARDCODED_CSL)

    # 4. snooker.org 抓取 - 斯诺克
    print("\n[数据源] snooker.org - 斯诺克")
    print("-" * 40)
    snooker_html = fetch_snooker_org()
    snooker_matches = parse_snooker_org(snooker_html)
    print(f"  [拉取] 斯诺克 -> {len(snooker_matches)} 场比赛")
    if snooker_matches:
        all_matches.extend(snooker_matches)
    else:
        snooker_fallback = [m for m in HARDCODED_OTHER if m["leagueType"] == "斯诺克"]
        if snooker_fallback:
            print(f"  [补充] 斯诺克硬编码 ({len(snooker_fallback)} 场)")
            all_matches.extend(snooker_fallback)

    # 5. 硬编码数据 - 仅补充未从API获取到的
    print("\n[数据源] 硬编码补充数据")
    print("-" * 40)

    # 电竞硬编码（仅补充未从Liquipedia获取到的）
    esports_fallback = []
    for m in HARDCODED_ESPORTS_FALLBACK:
        lt = m["leagueType"]
        if lt not in liquipedia_success:
            esports_fallback.append(m)
    if esports_fallback:
        print(f"  [补充] 电竞硬编码 ({len(esports_fallback)} 场): {[m['leagueType'] for m in esports_fallback]}")
        all_matches.extend(esports_fallback)

    # 其他分类（乒乓球、羽毛球等，排除斯诺克）
    other_fallback = [m for m in HARDCODED_OTHER if m["leagueType"] != "斯诺克"]
    if other_fallback:
        print(f"  [补充] 其他分类 ({len(other_fallback)} 场): {[m['leagueType'] for m in other_fallback]}")
        all_matches.extend(other_fallback)

    # 6. 过滤和排序
    today = datetime.now(BJ_TZ).strftime("%Y-%m-%d")
    all_matches = [m for m in all_matches if m["date"] >= today]

    seen = set()
    deduped = []
    for m in all_matches:
        key = (m["date"], m["time"], m["homeTeam"], m["awayTeam"], m["leagueType"])
        if key not in seen:
            seen.add(key)
            deduped.append(m)
    all_matches = deduped

    category_order = {"电竞": 0, "篮球": 1, "足球": 2, "其他": 3}
    all_matches.sort(key=lambda m: (category_order.get(m["category"], 99), m["date"], m["time"]))

    # 7. 输出
    output = {
        "version": 2,
        "updatedAt": datetime.now(BJ_TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "matches": all_matches,
    }

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"[DONE] 共 {len(all_matches)} 场比赛写入 matches.json")
    cats = {}
    for m in all_matches:
        cats[m["category"]] = cats.get(m["category"], 0) + 1
    for cat, count in cats.items():
        print(f"  {cat}: {count} 场")
    print(f"  Liquipedia自动更新: {list(liquipedia_success)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
