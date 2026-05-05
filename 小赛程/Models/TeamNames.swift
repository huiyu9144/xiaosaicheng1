import Foundation

struct TeamNames {
    static let chineseAbbreviation: [String: String] = [
        "尼克斯": "尼克斯",
        "76人": "76人",
        "马刺": "马刺",
        "森林狼": "森林狼",
        "活塞": "活塞",
        "骑士": "骑士",
        "雷霆": "雷霆",
        "湖人": "湖人",
    ]

    static let englishName: [String: String] = [
        "尼克斯": "Knicks",
        "76人": "76ers",
        "马刺": "Spurs",
        "森林狼": "Timberwolves",
        "活塞": "Pistons",
        "骑士": "Cavaliers",
        "雷霆": "Thunder",
        "湖人": "Lakers",
        "克雷莫纳": "Cremonese",
        "拉齐奥": "Lazio",
        "塞维利亚": "Sevilla",
        "皇家社会": "Real Sociedad",
        "埃弗顿": "Everton",
        "曼城": "Man City",
        "青岛西海岸": "Qingdao West Coast",
        "天津津门虎": "Tianjin Jinmen Tiger",
        "山东泰山": "Shandong Taishan",
        "上海申花": "Shanghai Shenhua",
        "辽宁铁人": "Liaoning Ironman",
        "成都蓉城": "Chengdu Rongcheng",
        "武汉三镇": "Wuhan Three Towns",
        "青岛海牛": "Qingdao Hainiu",
        "上海海港": "Shanghai Port",
        "深圳新鹏城": "Shenzhen Peng City",
        "北京国安": "Beijing Guoan",
        "大连英博": "Dalian Yingbo",
        "墨菲": "S. Murphy",
        "吴宜泽": "Wu Yize",
        "中国": "China",
        "澳大利亚": "Australia",
    ]

    static let englishToChinese: [String: String] = [
        "Knicks": "尼克斯",
        "76ers": "76人",
        "Spurs": "马刺",
        "Timberwolves": "森林狼",
        "Pistons": "活塞",
        "Cavaliers": "骑士",
        "Thunder": "雷霆",
        "Lakers": "湖人",
        "Cremonese": "克雷莫纳",
        "Lazio": "拉齐奥",
        "Sevilla": "塞维利亚",
        "Real Sociedad": "皇家社会",
        "Everton": "埃弗顿",
        "Man City": "曼城",
        "Qingdao West Coast": "青岛西海岸",
        "Tianjin Jinmen Tiger": "天津津门虎",
        "Shandong Taishan": "山东泰山",
        "Shanghai Shenhua": "上海申花",
        "Liaoning Ironman": "辽宁铁人",
        "Chengdu Rongcheng": "成都蓉城",
        "Wuhan Three Towns": "武汉三镇",
        "Qingdao Hainiu": "青岛海牛",
        "Shanghai Port": "上海海港",
        "Shenzhen Peng City": "深圳新鹏城",
        "Beijing Guoan": "北京国安",
        "Dalian Yingbo": "大连英博",
        "S. Murphy": "墨菲",
        "Wu Yize": "吴宜泽",
        "China": "中国",
        "Australia": "澳大利亚",
    ]

    static func localizedName(_ name: String, locale: AppLocale) -> String {
        if locale.isChinese {
            if let abbr = chineseAbbreviation[name] {
                return abbr
            }
            if let cn = englishToChinese[name] {
                return cn
            }
            return name
        } else {
            return englishName[name] ?? name
        }
    }
}
