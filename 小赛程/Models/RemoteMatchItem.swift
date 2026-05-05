import Foundation

struct RemoteMatchData: Codable {
    let version: Int
    let updatedAt: String
    let matches: [RemoteMatchItem]
}

struct RemoteMatchItem: Codable {
    let league: String
    let leagueType: String
    let matchStage: String?
    let leagueRound: Int?
    let homeTeam: String
    let awayTeam: String
    let time: String
    let date: String
    let category: String
    let isImportant: Bool
    let status: String
}

extension RemoteMatchItem {
    func toGameMatch() -> GameMatch? {
        guard let leagueType = LeagueType(rawValue: leagueType),
              let category = GameCategory(rawValue: category),
              let status = MatchStatus(rawValue: status) else {
            return nil
        }

        let matchStage = matchStage.flatMap { MatchStage(rawValue: $0) }

        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        dateFormatter.timeZone = TimeZone(identifier: "Asia/Shanghai")
        guard let date = dateFormatter.date(from: self.date) else { return nil }

        return GameMatch(
            league: league,
            leagueType: leagueType,
            matchStage: matchStage,
            leagueRound: leagueRound,
            homeTeam: homeTeam,
            awayTeam: awayTeam,
            time: time,
            date: date,
            category: category,
            isImportant: isImportant,
            status: status
        )
    }
}
