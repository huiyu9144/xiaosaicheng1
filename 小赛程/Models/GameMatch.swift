import Foundation

enum GameCategory: String, CaseIterable, Identifiable, Codable {
    case all = "全部"
    case esports = "电竞"
    case basketball = "篮球"
    case football = "足球"
    case other = "其他"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .all: return "square.grid.2x2"
        case .esports: return "gamecontroller.fill"
        case .basketball: return "basketball.fill"
        case .football: return "soccerball"
        case .other: return "trophy.fill"
        }
    }

    var sortOrder: Int {
        switch self {
        case .esports: return 0
        case .basketball: return 1
        case .football: return 2
        case .other: return 3
        case .all: return 4
        }
    }

    func localizedName(_ locale: AppLocale) -> String {
        switch self {
        case .all: return locale.loc("CategoryAll")
        case .esports: return locale.loc("CategoryEsports")
        case .basketball: return locale.loc("CategoryBasketball")
        case .football: return locale.loc("CategoryFootball")
        case .other: return locale.loc("CategoryOther")
        }
    }
}

enum LeagueType: String, Codable {
    case premierLeague = "英超"
    case laLiga = "西甲"
    case serieA = "意甲"
    case championsLeague = "欧冠"
    case bundesliga = "德甲"
    case csl = "中超"
    case worldSnooker = "斯诺克"
    case tableTennis = "乒乓球"
    case badminton = "羽毛球"
    case diving = "跳水"
    case tennis = "网球"
    case vctCN = "VCT CN"
    case vctPacific = "VCT Pacific"
    case vctEMEA = "VCT EMEA"
    case vctAmericas = "VCT Americas"
    case lolLPL = "LPL"
    case lolLCK = "LCK"
    case lolLEC = "LEC"
    case lolMSI = "MSI"
    case dota2TI = "TI"
    case dota2ACL = "ACL"
    case pubgPGS = "PGS"
    case pubgPCL = "PCL"
    case pubgPNC = "PNC"
    case nba = "NBA"

    var gameName: String {
        switch self {
        case .vctCN, .vctPacific, .vctEMEA, .vctAmericas:
            return "瓦"
        case .lolLPL, .lolLCK, .lolLEC, .lolMSI:
            return "LOL"
        case .dota2TI, .dota2ACL:
            return "DOTA2"
        case .pubgPGS, .pubgPCL, .pubgPNC:
            return "PUBG"
        case .nba:
            return "NBA"
        default:
            return rawValue
        }
    }

    func localizedName(_ locale: AppLocale) -> String {
        switch self {
        case .premierLeague: return locale.loc("LeaguePremierLeague")
        case .laLiga: return locale.loc("LeagueLaLiga")
        case .serieA: return locale.loc("LeagueSerieA")
        case .championsLeague: return locale.loc("LeagueChampionsLeague")
        case .bundesliga: return locale.loc("LeagueBundesliga")
        case .csl: return locale.loc("LeagueCSL")
        case .worldSnooker: return locale.loc("LeagueWorldSnooker")
        case .tableTennis: return locale.loc("LeagueTableTennis")
        case .badminton: return locale.loc("LeagueBadminton")
        case .vctCN: return locale.loc("LeagueVCTCN")
        case .lolLCK: return locale.loc("LeagueLCK")
        case .lolLPL: return locale.loc("LeagueLPL")
        case .pubgPCL: return locale.loc("LeaguePCL")
        case .pubgPGS: return locale.loc("LeaguePGS")
        case .dota2TI: return locale.loc("LeagueDOTA2")
        case .nba: return locale.loc("LeagueNBA")
        default: return rawValue
        }
    }
}

enum MatchStage: String, Codable {
    case groupStage = "小组赛"
    case quarterfinal = "1/4决赛"
    case semifinal = "半决赛"
    case final = "决赛"
    case roundOf16 = "16强"
    case roundOf32 = "32强"
    case playoffs = "季后赛"
    case regularSeason = "常规赛"
    case upperBracketQuarterfinal = "胜者组1/4决赛"
    case upperBracketSemifinal = "胜者组半决赛"
    case upperBracketFinal = "胜者组决赛"
    case lowerBracketRound1 = "败者组第一轮"
    case lowerBracketRound2 = "败者组第二轮"
    case lowerBracketQuarterfinal = "败者组1/4决赛"
    case lowerBracketSemifinal = "败者组半决赛"
    case lowerBracketFinal = "败者组决赛"
    case conferenceSemifinal = "分区半决赛"
    case conferenceFinal = "分区决赛"
    case nbaFinal = "总决赛"

    func localizedName(_ locale: AppLocale) -> String {
        switch self {
        case .lowerBracketQuarterfinal: return locale.loc("StageLowerBracketQuarterfinal")
        case .lowerBracketSemifinal: return locale.loc("StageLowerBracketSemifinal")
        case .lowerBracketFinal: return locale.loc("StageLowerBracketFinal")
        case .upperBracketFinal: return locale.loc("StageUpperBracketFinal")
        case .final: return locale.loc("StageFinal")
        case .regularSeason: return locale.loc("StageRegularSeason")
        case .groupStage: return locale.loc("StageGroupStage")
        case .roundOf32: return locale.loc("StageRoundOf32")
        case .roundOf16: return locale.loc("StageRoundOf16")
        case .conferenceSemifinal: return locale.loc("StageConferenceSemifinal")
        default: return rawValue
        }
    }
}

struct GameMatch: Identifiable, Codable {
    let id: UUID
    let league: String
    let leagueType: LeagueType
    let matchStage: MatchStage?
    let leagueRound: Int?
    let homeTeam: String
    let awayTeam: String
    let time: String
    let date: Date
    let category: GameCategory
    let isImportant: Bool
    let status: MatchStatus

    init(id: UUID = UUID(), league: String, leagueType: LeagueType, matchStage: MatchStage?, leagueRound: Int? = nil, homeTeam: String, awayTeam: String, time: String, date: Date, category: GameCategory, isImportant: Bool, status: MatchStatus) {
        self.id = id
        self.league = league
        self.leagueType = leagueType
        self.matchStage = matchStage
        self.leagueRound = leagueRound
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.time = time
        self.date = date
        self.category = category
        self.isImportant = isImportant
        self.status = status
    }

    var formattedDate: String {
        let calendar = Calendar.current
        if calendar.isDateInToday(date) {
            return "今天"
        } else if calendar.isDateInTomorrow(date) {
            return "明天"
        } else {
            let formatter = DateFormatter()
            formatter.dateFormat = "M月d日"
            return formatter.string(from: date)
        }
    }

    var displayLeague: String {
        var result = ""
        if !league.isEmpty {
            result = league
        } else {
            result = leagueType.rawValue
        }
        if let round = leagueRound, (category == .football || category == .basketball) {
            result += " \(round)轮"
        }
        return result
    }

    var gamePrefix: String {
        switch category {
        case .esports:
            return leagueType.gameName
        case .basketball:
            return ""
        case .football:
            return ""
        case .other:
            return leagueType.rawValue
        case .all:
            return ""
        }
    }

    func localizedDisplayLeague(_ locale: AppLocale) -> String {
        if !league.isEmpty {
            return league
        }
        var result = leagueType.localizedName(locale)
        if let round = leagueRound, (category == .football || category == .basketball) {
            if locale.isChinese {
                result += " \(round)轮"
            } else {
                result += " R\(round)"
            }
        }
        return result
    }

    func localizedGamePrefix(_ locale: AppLocale) -> String {
        switch category {
        case .esports:
            return leagueType.gameName
        case .basketball:
            return ""
        case .football:
            return ""
        case .other:
            return leagueType.localizedName(locale)
        case .all:
            return ""
        }
    }

    func localizedStage(_ locale: AppLocale) -> String? {
        matchStage?.localizedName(locale)
    }

    func localizedTime(_ locale: AppLocale) -> String {
        locale.convertTime(time, date: date)
    }

    func localizedDate(_ locale: AppLocale) -> String {
        locale.formattedDate(date)
    }

    func localizedHomeTeam(_ locale: AppLocale) -> String {
        TeamNames.localizedName(homeTeam, locale: locale)
    }

    func localizedAwayTeam(_ locale: AppLocale) -> String {
        TeamNames.localizedName(awayTeam, locale: locale)
    }

    var isTeamMatchup: Bool {
        let nonTeamKeywords = ["阶段", "组", "小组"]
        for keyword in nonTeamKeywords {
            if homeTeam.contains(keyword) || awayTeam.contains(keyword) {
                return false
            }
        }
        return !homeTeam.isEmpty && !awayTeam.isEmpty
    }

    func isToday(_ locale: AppLocale) -> Bool {
        locale.isToday(date)
    }

    func isTomorrow(_ locale: AppLocale) -> Bool {
        locale.isTomorrow(date)
    }

    func isLive() -> Bool {
        if status == .live {
            let now = Date()
            let calendar = Calendar.current
            guard calendar.isDateInToday(date) else { return false }

            let timeComponents = time.split(separator: ":").compactMap { Int($0) }
            guard timeComponents.count == 2 else { return false }
            let hour = timeComponents[0]
            let minute = timeComponents[1]

            var matchComponents = calendar.dateComponents([.year, .month, .day], from: date)
            matchComponents.hour = hour
            matchComponents.minute = minute

            guard let matchTime = calendar.date(from: matchComponents) else { return false }

            let matchEndTime = calendar.date(byAdding: .hour, value: 3, to: matchTime) ?? matchTime
            return now >= matchTime && now <= matchEndTime
        }
        return false
    }
}

enum MatchStatus: String, Codable {
    case upcoming
    case live
    case finished
}

struct CachedMatchData: Codable {
    let matches: [GameMatch]
    let cachedAt: Date
    let dataSource: String

    var isExpired: Bool {
        let calendar = Calendar.current
        guard let tomorrow = calendar.date(byAdding: .day, value: 1, to: cachedAt) else { return true }
        return Date() >= calendar.startOfDay(for: tomorrow)
    }
}
