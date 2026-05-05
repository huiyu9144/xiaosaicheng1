import Foundation
import Combine

class MatchService: ObservableObject {
    @Published var matches: [GameMatch] = []
    @Published var isLoading = false
    @Published var dataSourceInfo: String = ""

    private let userDefaultsKey = "lastSelectedCategory"
    private let cacheKey = "cachedMatchData_v10"
    private let remoteFetchKey = "lastRemoteFetchAttempt"

    private var remoteURL: String {
        UserDefaults.standard.string(forKey: "remoteDataURL")
            ?? "https://raw.githubusercontent.com/huiyu9144/xiaosaicheng1/main/matches.json"
    }

    func fetchMatches() {
        if let cachedData = loadCachedData(), !cachedData.isExpired {
            self.matches = cachedData.matches
            self.dataSourceInfo = cachedData.dataSource
            updateLiveStatus()
            return
        }

        isLoading = true

        if !remoteURL.isEmpty {
            fetchRemoteData()
        } else {
            fallbackToLocalData()
        }
    }

    func refreshCache() {
        UserDefaults.standard.removeObject(forKey: cacheKey)
        UserDefaults.standard.removeObject(forKey: remoteFetchKey)
        isLoading = true
        matches = []

        if !remoteURL.isEmpty {
            fetchRemoteData()
        } else {
            fallbackToLocalData()
        }
    }

    private func fetchRemoteData() {
        guard let url = URL(string: remoteURL) else {
            fallbackToLocalData()
            return
        }

        var request = URLRequest(url: url)
        request.cachePolicy = .reloadIgnoringLocalCacheData
        request.timeoutInterval = 10

        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            guard let self = self else { return }

            if let error = error {
                print("[小赛程] 远程数据拉取失败: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self.fallbackToLocalData()
                }
                return
            }

            guard let data = data else {
                DispatchQueue.main.async {
                    self.fallbackToLocalData()
                }
                return
            }

            DispatchQueue.main.async {
                do {
                    let remoteData = try JSONDecoder().decode(RemoteMatchData.self, from: data)
                    let gameMatches = remoteData.matches.compactMap { $0.toGameMatch() }

                    let calendar = Calendar.current
                    let todayStart = calendar.startOfDay(for: Date())
                    let filteredMatches = gameMatches
                        .filter { $0.date >= todayStart }
                        .sorted { match1, match2 in
                            if match1.category.sortOrder != match2.category.sortOrder {
                                return match1.category.sortOrder < match2.category.sortOrder
                            }
                            if match1.date != match2.date {
                                return match1.date < match2.date
                            }
                            return match1.time < match2.time
                        }

                    self.matches = filteredMatches
                    self.dataSourceInfo = "远程数据 v\(remoteData.version) 更新于 \(remoteData.updatedAt)"
                    self.saveCachedData(filteredMatches, source: "remote_v\(remoteData.version)")
                    self.updateLiveStatus()
                    self.isLoading = false
                    UserDefaults.standard.set(Date(), forKey: self.remoteFetchKey)
                } catch {
                    print("[小赛程] 远程数据解析失败: \(error)")
                    self.fallbackToLocalData()
                }
            }
        }.resume()
    }

    private func fallbackToLocalData() {
        DispatchQueue.global().asyncAfter(deadline: .now() + 0.3) { [weak self] in
            self?.loadRealData()
            DispatchQueue.main.async {
                self?.isLoading = false
            }
        }
    }

    private func loadCachedData() -> CachedMatchData? {
        guard let data = UserDefaults.standard.data(forKey: cacheKey) else { return nil }
        return try? JSONDecoder().decode(CachedMatchData.self, from: data)
    }

    private func saveCachedData(_ matches: [GameMatch], source: String = "local") {
        let cachedData = CachedMatchData(
            matches: matches,
            cachedAt: Date(),
            dataSource: source
        )
        if let encoded = try? JSONEncoder().encode(cachedData) {
            UserDefaults.standard.set(encoded, forKey: cacheKey)
        }
    }

    private func updateLiveStatus() {
        let now = Date()
        let calendar = Calendar.current

        for i in 0..<matches.count {
            var match = matches[i]
            if match.status == .upcoming || match.status == .live {
                let timeComponents = match.time.split(separator: ":").compactMap { Int($0) }
                guard timeComponents.count == 2 else { continue }
                let hour = timeComponents[0]
                let minute = timeComponents[1]

                var matchComponents = calendar.dateComponents([.year, .month, .day], from: match.date)
                matchComponents.hour = hour
                matchComponents.minute = minute

                guard let matchTime = calendar.date(from: matchComponents) else { continue }

                let matchEndTime = calendar.date(byAdding: .hour, value: 3, to: matchTime) ?? matchTime

                if now >= matchTime && now <= matchEndTime && calendar.isDateInToday(match.date) {
                    match = GameMatch(
                        id: match.id,
                        league: match.league,
                        leagueType: match.leagueType,
                        matchStage: match.matchStage,
                        leagueRound: match.leagueRound,
                        homeTeam: match.homeTeam,
                        awayTeam: match.awayTeam,
                        time: match.time,
                        date: match.date,
                        category: match.category,
                        isImportant: match.isImportant,
                        status: .live
                    )
                } else if now > matchEndTime && calendar.isDateInToday(match.date) {
                    match = GameMatch(
                        id: match.id,
                        league: match.league,
                        leagueType: match.leagueType,
                        matchStage: match.matchStage,
                        leagueRound: match.leagueRound,
                        homeTeam: match.homeTeam,
                        awayTeam: match.awayTeam,
                        time: match.time,
                        date: match.date,
                        category: match.category,
                        isImportant: match.isImportant,
                        status: .finished
                    )
                }
                matches[i] = match
            }
        }
    }

    private func loadRealData() {
        let calendar = Calendar.current
        let may5 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 5))!
        let may6 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 6))!
        let may7 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 7))!
        let may8 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 8))!
        let may9 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 9))!
        let may10 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 10))!
        let may12 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 12))!
        let may13 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 13))!
        let may19 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 19))!
        let may20 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 20))!
        let may26 = calendar.date(from: DateComponents(year: 2026, month: 5, day: 26))!

        let unsortedMatches: [GameMatch] = [
            // MARK: - 电竞

            // VCT CN 2026 第一赛段季后赛 - liquipedia.net/valorant
            GameMatch(
                league: "VCT CN",
                leagueType: .vctCN,
                matchStage: .lowerBracketQuarterfinal,
                homeTeam: "JDG",
                awayTeam: "DRG",
                time: "17:00",
                date: may5,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "VCT CN",
                leagueType: .vctCN,
                matchStage: .lowerBracketQuarterfinal,
                homeTeam: "AG",
                awayTeam: "TYL",
                time: "19:00",
                date: may5,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "VCT CN",
                leagueType: .vctCN,
                matchStage: .upperBracketFinal,
                homeTeam: "XLG",
                awayTeam: "EDG",
                time: "17:00",
                date: may8,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "VCT CN",
                leagueType: .vctCN,
                matchStage: .lowerBracketSemifinal,
                homeTeam: "TBD",
                awayTeam: "TBD",
                time: "19:00",
                date: may8,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "VCT CN",
                leagueType: .vctCN,
                matchStage: .lowerBracketFinal,
                homeTeam: "TBD",
                awayTeam: "TBD",
                time: "17:00",
                date: may9,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "VCT CN",
                leagueType: .vctCN,
                matchStage: .final,
                homeTeam: "TBD",
                awayTeam: "TBD",
                time: "17:00",
                date: may10,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),

            // LOL - LCK 2026 常规赛 - egamersworld.com/lol
            GameMatch(
                league: "LCK",
                leagueType: .lolLCK,
                matchStage: .regularSeason,
                homeTeam: "GEN",
                awayTeam: "NS",
                time: "16:00",
                date: may6,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "LCK",
                leagueType: .lolLCK,
                matchStage: .regularSeason,
                homeTeam: "HLE",
                awayTeam: "SOOP",
                time: "18:00",
                date: may6,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),

            // LOL - LPL 2026 第二赛段常规赛 - egamersworld.com/lol
            GameMatch(
                league: "LPL",
                leagueType: .lolLPL,
                matchStage: .regularSeason,
                homeTeam: "WE",
                awayTeam: "iG",
                time: "17:00",
                date: may6,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "LPL",
                leagueType: .lolLPL,
                matchStage: .regularSeason,
                homeTeam: "TES",
                awayTeam: "JDG",
                time: "19:00",
                date: may6,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),

            // PUBG - PCL 2026 春季赛 S阶段 - weibo.com/pcl赛事
            GameMatch(
                league: "PCL",
                leagueType: .pubgPCL,
                matchStage: .groupStage,
                homeTeam: "S阶段",
                awayTeam: "B组&C组",
                time: "18:00",
                date: may5,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "PCL",
                leagueType: .pubgPCL,
                matchStage: .groupStage,
                homeTeam: "S阶段",
                awayTeam: "C组&A组",
                time: "18:00",
                date: may6,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),

            // PUBG - PGS 2026 第二赛季 - 5月20日开始
            GameMatch(
                league: "PGS",
                leagueType: .pubgPGS,
                matchStage: .groupStage,
                homeTeam: "PGS 4",
                awayTeam: "小组赛",
                time: "18:00",
                date: may20,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),

            // DOTA2 - DreamLeague Season 29 - May 13-24
            GameMatch(
                league: "DreamLeague",
                leagueType: .dota2TI,
                matchStage: .groupStage,
                homeTeam: "S29",
                awayTeam: "小组赛",
                time: "18:00",
                date: may13,
                category: .esports,
                isImportant: true,
                status: .upcoming
            ),

            // MARK: - 篮球

            // NBA 2026 季后赛 分区半决赛 - nba.com / weibo
            GameMatch(
                league: "NBA",
                leagueType: .nba,
                matchStage: .conferenceSemifinal,
                homeTeam: "尼克斯",
                awayTeam: "76人",
                time: "08:00",
                date: may5,
                category: .basketball,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "NBA",
                leagueType: .nba,
                matchStage: .conferenceSemifinal,
                homeTeam: "马刺",
                awayTeam: "森林狼",
                time: "09:30",
                date: may5,
                category: .basketball,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "NBA",
                leagueType: .nba,
                matchStage: .conferenceSemifinal,
                homeTeam: "活塞",
                awayTeam: "骑士",
                time: "07:00",
                date: may6,
                category: .basketball,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "NBA",
                leagueType: .nba,
                matchStage: .conferenceSemifinal,
                homeTeam: "雷霆",
                awayTeam: "湖人",
                time: "08:30",
                date: may6,
                category: .basketball,
                isImportant: true,
                status: .upcoming
            ),

            // MARK: - 足球

            GameMatch(
                league: "",
                leagueType: .serieA,
                matchStage: .regularSeason,
                leagueRound: 35,
                homeTeam: "克雷莫纳",
                awayTeam: "拉齐奥",
                time: "00:30",
                date: may5,
                category: .football,
                isImportant: false,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .laLiga,
                matchStage: .regularSeason,
                leagueRound: 34,
                homeTeam: "塞维利亚",
                awayTeam: "皇家社会",
                time: "03:00",
                date: may5,
                category: .football,
                isImportant: false,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .premierLeague,
                matchStage: .regularSeason,
                leagueRound: 35,
                homeTeam: "埃弗顿",
                awayTeam: "曼城",
                time: "03:00",
                date: may5,
                category: .football,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .csl,
                matchStage: .regularSeason,
                leagueRound: 10,
                homeTeam: "青岛西海岸",
                awayTeam: "天津津门虎",
                time: "19:00",
                date: may5,
                category: .football,
                isImportant: false,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .csl,
                matchStage: .regularSeason,
                leagueRound: 10,
                homeTeam: "山东泰山",
                awayTeam: "上海申花",
                time: "19:35",
                date: may5,
                category: .football,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .csl,
                matchStage: .regularSeason,
                leagueRound: 10,
                homeTeam: "辽宁铁人",
                awayTeam: "成都蓉城",
                time: "19:35",
                date: may5,
                category: .football,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .csl,
                matchStage: .regularSeason,
                leagueRound: 10,
                homeTeam: "武汉三镇",
                awayTeam: "青岛海牛",
                time: "19:00",
                date: may6,
                category: .football,
                isImportant: false,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .csl,
                matchStage: .regularSeason,
                leagueRound: 10,
                homeTeam: "上海海港",
                awayTeam: "深圳新鹏城",
                time: "19:35",
                date: may6,
                category: .football,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "",
                leagueType: .csl,
                matchStage: .regularSeason,
                leagueRound: 10,
                homeTeam: "北京国安",
                awayTeam: "大连英博",
                time: "19:35",
                date: may6,
                category: .football,
                isImportant: true,
                status: .upcoming
            ),

            // MARK: - 其他

            GameMatch(
                league: "世锦赛",
                leagueType: .worldSnooker,
                matchStage: .final,
                homeTeam: "墨菲",
                awayTeam: "吴宜泽",
                time: "02:00",
                date: may5,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "世乒赛",
                leagueType: .tableTennis,
                matchStage: .roundOf32,
                homeTeam: "中国",
                awayTeam: "澳大利亚",
                time: "17:00",
                date: may5,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "世乒赛",
                leagueType: .tableTennis,
                matchStage: .roundOf16,
                homeTeam: "中国",
                awayTeam: "TBD",
                time: "17:00",
                date: may6,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "世乒赛",
                leagueType: .tableTennis,
                matchStage: .roundOf16,
                homeTeam: "中国",
                awayTeam: "TBD",
                time: "17:00",
                date: may7,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "世乒赛",
                leagueType: .tableTennis,
                matchStage: .quarterfinal,
                homeTeam: "中国",
                awayTeam: "TBD",
                time: "17:00",
                date: may8,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "世乒赛",
                leagueType: .tableTennis,
                matchStage: .semifinal,
                homeTeam: "中国",
                awayTeam: "TBD",
                time: "17:00",
                date: may9,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "世乒赛",
                leagueType: .tableTennis,
                matchStage: .final,
                homeTeam: "中国",
                awayTeam: "TBD",
                time: "19:00",
                date: may10,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "泰国公开赛",
                leagueType: .badminton,
                matchStage: .roundOf32,
                homeTeam: "石宇奇",
                awayTeam: "陈雨菲",
                time: "10:00",
                date: may12,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "马来西亚大师赛",
                leagueType: .badminton,
                matchStage: .roundOf32,
                homeTeam: "李诗沣",
                awayTeam: "王祉怡",
                time: "10:00",
                date: may19,
                category: .other,
                isImportant: true,
                status: .upcoming
            ),
            GameMatch(
                league: "新加坡公开赛",
                leagueType: .badminton,
                matchStage: .roundOf32,
                homeTeam: "何济霆",
                awayTeam: "刘圣书",
                time: "10:00",
                date: may26,
                category: .other,
                isImportant: true,
                status: .upcoming
            )
        ]

        let sortedMatches = unsortedMatches.sorted { match1, match2 in
            if match1.category.sortOrder != match2.category.sortOrder {
                return match1.category.sortOrder < match2.category.sortOrder
            }
            if match1.date != match2.date {
                return match1.date < match2.date
            }
            return match1.time < match2.time
        }

        let todayStart = calendar.startOfDay(for: Date())
        let filteredMatches = sortedMatches.filter { $0.date >= todayStart }

        DispatchQueue.main.async { [weak self] in
            self?.matches = filteredMatches
            self?.dataSourceInfo = "本地内置数据"
            self?.saveCachedData(filteredMatches, source: "local_builtin")
            self?.updateLiveStatus()
        }
    }
}