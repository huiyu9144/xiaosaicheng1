import SwiftUI
import Observation

@Observable
class AppLocale {
    var language: String {
        didSet {
            UserDefaults.standard.set(language, forKey: "appLanguage")
        }
    }
    var timezone: String {
        didSet {
            UserDefaults.standard.set(timezone, forKey: "appTimezone")
        }
    }

    static let shared = AppLocale()

    private init() {
        let deviceLanguage = Locale.current.language.languageCode?.identifier ?? "en"
        let isChineseLanguage = deviceLanguage == "zh"

        if isChineseLanguage {
            language = UserDefaults.standard.string(forKey: "appLanguage") ?? "zh"
            timezone = UserDefaults.standard.string(forKey: "appTimezone") ?? "Asia/Shanghai"
        } else {
            language = UserDefaults.standard.string(forKey: "appLanguage") ?? "en"
            let deviceTimezone = TimeZone.current.identifier
            let supportedTimezones = [
                "Asia/Shanghai", "Asia/Tokyo", "Asia/Seoul", "America/New_York",
                "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Singapore",
                "Asia/Hong_Kong", "Australia/Sydney"
            ]
            if supportedTimezones.contains(deviceTimezone) {
                timezone = UserDefaults.standard.string(forKey: "appTimezone") ?? deviceTimezone
            } else {
                timezone = UserDefaults.standard.string(forKey: "appTimezone") ?? "America/New_York"
            }
        }
    }

    var currentTimezone: TimeZone {
        TimeZone(identifier: timezone) ?? .current
    }

    var isChinese: Bool {
        language == "zh"
    }

    func loc(_ key: String) -> String {
        let bundlePath = Bundle.main.path(forResource: language, ofType: "lproj")
        let bundle = bundlePath.flatMap(Bundle.init(path:)) ?? Bundle.main
        return NSLocalizedString(key, bundle: bundle, comment: "")
    }

    func convertTime(_ time: String, date: Date) -> String {
        guard let tz = TimeZone(identifier: timezone) else { return time }
        let sourceTZ = TimeZone(identifier: "Asia/Shanghai")!

        let parts = time.split(separator: ":").compactMap { Int($0) }
        guard parts.count == 2 else { return time }

        var calendar = Calendar.current
        calendar.timeZone = sourceTZ
        var comps = calendar.dateComponents([.year, .month, .day], from: date)
        comps.hour = parts[0]
        comps.minute = parts[1]

        guard let sourceDate = calendar.date(from: comps) else { return time }

        calendar.timeZone = tz
        let targetComps = calendar.dateComponents([.hour, .minute], from: sourceDate)
        return String(format: "%02d:%02d", targetComps.hour ?? 0, targetComps.minute ?? 0)
    }

    func formattedDate(_ date: Date) -> String {
        var calendar = Calendar.current
        calendar.timeZone = currentTimezone

        let today = calendar.startOfDay(for: Date())
        let targetDay = calendar.startOfDay(for: date)

        if targetDay == today {
            return loc("Today")
        } else if let tomorrow = calendar.date(byAdding: .day, value: 1, to: today), targetDay == tomorrow {
            return loc("Tomorrow")
        } else {
            let fmt = DateFormatter()
            fmt.timeZone = currentTimezone
            if isChinese {
                fmt.dateFormat = "M月d日"
            } else {
                fmt.dateFormat = "MMM d"
            }
            return fmt.string(from: date)
        }
    }

    func isToday(_ date: Date) -> Bool {
        var calendar = Calendar.current
        calendar.timeZone = currentTimezone
        return calendar.isDateInToday(date)
    }

    func isTomorrow(_ date: Date) -> Bool {
        var calendar = Calendar.current
        calendar.timeZone = currentTimezone
        return calendar.isDateInTomorrow(date)
    }
}
