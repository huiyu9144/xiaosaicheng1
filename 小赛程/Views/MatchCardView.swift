import SwiftUI

struct MatchCardView: View {
    let match: GameMatch
    let refreshTrigger: UUID?
    @Environment(AppLocale.self) var locale

    var body: some View {
        HStack(alignment: .center, spacing: 12) {
            Image(systemName: categoryIconName)
                .font(.system(size: 20))
                .foregroundColor(categoryColor)
                .frame(width: 32)

            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 4) {
                    let prefix = match.localizedGamePrefix(locale)
                    if !prefix.isEmpty {
                        Text(prefix)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    }

                    Text(match.localizedDisplayLeague(locale))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .lineLimit(1)

                    if let stage = match.localizedStage(locale) {
                        Text(stage)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    }
                }

                HStack(spacing: 4) {
                    Text(match.localizedHomeTeam(locale))
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .lineLimit(1)

                    if match.isTeamMatchup {
                        Text(locale.loc("vs"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Text(match.localizedAwayTeam(locale))
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .lineLimit(1)
                }
            }
            .layoutPriority(-1)

            Spacer()

            VStack(alignment: .trailing, spacing: 2) {
                Text(match.localizedTime(locale))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.white)

                Text(dateDisplayText)
                    .font(.caption2)
                    .foregroundColor(dateColor)
            }
            .layoutPriority(1)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color(.systemGray6))
        .cornerRadius(12)
        .id(refreshTrigger)
    }

    private var dateDisplayText: String {
        if match.status == .live {
            return locale.loc("Live")
        }
        if match.status == .finished {
            return locale.loc("Finished")
        }
        return match.localizedDate(locale)
    }

    private var dateColor: Color {
        if match.status == .live {
            return Color(red: 255/255, green: 100/255, blue: 100/255)
        }
        if match.status == .finished {
            return .gray
        }
        if match.isToday(locale) {
            return .green
        } else if match.isTomorrow(locale) {
            return .cyan
        } else {
            return .secondary
        }
    }

    private var categoryIconName: String {
        switch match.category {
        case .esports:
            return "gamecontroller.fill"
        case .basketball:
            return "basketball.fill"
        case .football:
            return "soccerball"
        case .other:
            return "trophy.fill"
        case .all:
            return "square.grid.2x2"
        }
    }

    private var categoryColor: Color {
        switch match.category {
        case .esports:
            return Color(red: 160/255, green: 120/255, blue: 220/255)
        case .basketball:
            return .orange
        case .football:
            return .green
        case .other:
            return .yellow
        case .all:
            return .gray
        }
    }
}
