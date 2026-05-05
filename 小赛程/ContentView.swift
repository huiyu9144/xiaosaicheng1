import SwiftUI
import Combine

struct ContentView: View {
    @StateObject private var matchService = MatchService()
    @Environment(AppLocale.self) var locale
    @State private var searchText = ""
    @AppStorage("lastSelectedCategory") private var selectedCategoryRaw: String = GameCategory.esports.rawValue
    @State private var selectedCategory: GameCategory = .esports
    @State private var isSearching = false
    @State private var showSettings = false
    @State private var isRefreshing = false
    @State private var refreshTrigger = UUID()

    private var filteredMatches: [GameMatch] {
        matchService.matches.filter { match in
            let matchesCategory = selectedCategory == .all || match.category == selectedCategory
            let matchesSearch = searchText.isEmpty ||
                match.homeTeam.localizedCaseInsensitiveContains(searchText) ||
                match.awayTeam.localizedCaseInsensitiveContains(searchText) ||
                match.league.localizedCaseInsensitiveContains(searchText)
            return matchesCategory && matchesSearch
        }
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)

                ScrollView {
                    VStack(spacing: 24) {
                        HeaderView(showSettings: $showSettings)

                        SearchBarView(searchText: $searchText)
                            .padding(.horizontal, 20)
                            .transition(.move(edge: .top))

                        CategoryFilterView(
                            categories: GameCategory.allCases,
                            selectedCategory: $selectedCategory
                        )
                        .padding(.horizontal, 20)

                        if isRefreshing {
                            RefreshIndicatorView()
                        }

                        MatchListView(matches: filteredMatches, isLoading: matchService.isLoading, refreshTrigger: refreshTrigger)
                    }
                    .padding(.top, 20)
                    .padding(.bottom, 100)
                }
                .refreshable {
                    isRefreshing = true
                    refreshTrigger = UUID()
                    try? await Task.sleep(nanoseconds: 400_000_000)
                    isRefreshing = false
                }
            }
            .navigationBarHidden(true)
            .sheet(isPresented: $showSettings) {
                SettingsView()
                    .environmentObject(matchService)
            }
            .onAppear {
                if let category = GameCategory(rawValue: selectedCategoryRaw) {
                    selectedCategory = category
                }
                matchService.fetchMatches()
            }
            .onChange(of: selectedCategoryRaw) { _, newValue in
                if let category = GameCategory(rawValue: newValue) {
                    selectedCategory = category
                }
            }
            .onChange(of: selectedCategory) { _, newCategory in
                selectedCategoryRaw = newCategory.rawValue
            }
            .onReceive(MidnightRefreshTimer.shared.$shouldRefresh) { shouldRefresh in
                if shouldRefresh {
                    matchService.fetchMatches()
                }
            }
        }
    }
}

struct RefreshIndicatorView: View {
    var body: some View {
        HStack(spacing: 8) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                .scaleEffect(0.8)
        }
        .frame(height: 40)
        .padding(.top, 10)
    }
}

class MidnightRefreshTimer: ObservableObject {
    static let shared = MidnightRefreshTimer()

    @Published var shouldRefresh = false

    private var timer: Timer?
    private var lastRefreshDate: Date

    init() {
        lastRefreshDate = UserDefaults.standard.object(forKey: "lastRefreshDate") as? Date ?? Date()

        scheduleNextRefresh()

        timer = Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in
            self?.checkMidnight()
        }
    }

    private func scheduleNextRefresh() {
        let calendar = Calendar.current
        var components = calendar.dateComponents([.year, .month, .day], from: Date())
        components.day! += 1
        components.hour = 0
        components.minute = 0
        components.second = 0

        if let nextMidnight = calendar.date(from: components) {
            let interval = nextMidnight.timeIntervalSince(Date())
            DispatchQueue.main.asyncAfter(deadline: .now() + interval) { [weak self] in
                self?.triggerRefresh()
            }
        }
    }

    private func checkMidnight() {
        let calendar = Calendar.current
        if !calendar.isDate(lastRefreshDate, inSameDayAs: Date()) {
            triggerRefresh()
        }
    }

    private func triggerRefresh() {
        shouldRefresh = true
        lastRefreshDate = Date()
        UserDefaults.standard.set(lastRefreshDate, forKey: "lastRefreshDate")
        scheduleNextRefresh()

        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.shouldRefresh = false
        }
    }
}

struct HeaderView: View {
    @Binding var showSettings: Bool
    @Environment(AppLocale.self) var locale

    var body: some View {
        HStack {
            Text(locale.loc("Title"))
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.white)

            Spacer()

            Button {
                showSettings = true
            } label: {
                Image(systemName: "gearshape.fill")
                    .font(.system(size: 18))
                    .foregroundColor(.secondary)
            }
        }
        .padding(.horizontal, 20)
    }
}

struct MatchListView: View {
    let matches: [GameMatch]
    let isLoading: Bool
    let refreshTrigger: UUID

    var body: some View {
        if isLoading {
            LoadingView()
        } else if matches.isEmpty {
            EmptyStateView()
        } else {
            VStack(spacing: 12) {
                ForEach(matches) { match in
                    MatchCardView(match: match, refreshTrigger: refreshTrigger)
                        .padding(.horizontal, 20)
                }
            }
            .animation(.easeInOut(duration: 0.2), value: matches.map(\.id))
        }
    }
}

struct LoadingView: View {
    @Environment(AppLocale.self) var locale

    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
            Text(locale.isChinese ? "加载中..." : "Loading...")
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 40)
    }
}

struct EmptyStateView: View {
    @Environment(AppLocale.self) var locale

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "calendar.badge.exclamationmark")
                .font(.system(size: 64))
                .foregroundColor(.secondary)
            Text(locale.loc("EmptyState"))
                .font(.title)
                .foregroundColor(.white)
            Text(locale.isChinese ? "当前筛选条件下没有找到比赛" : "No matches found for current filter")
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 60)
    }
}

#Preview {
    ContentView()
}

struct SettingsView: View {
    @Environment(AppLocale.self) var locale
    @EnvironmentObject var matchService: MatchService
    @Environment(\.dismiss) private var dismiss
    @State private var isRefreshing = false

    private let languages: [(String, String)] = [
        ("zh", "中文"),
        ("en", "English"),
    ]

    private let timezones: [(String, String)] = [
        ("Asia/Shanghai", "北京时间 (UTC+8)"),
        ("Asia/Tokyo", "东京时间 (UTC+9)"),
        ("Asia/Seoul", "首尔时间 (UTC+9)"),
        ("America/New_York", "纽约时间 (UTC-4)"),
        ("Europe/London", "伦敦时间 (UTC+1)"),
        ("Europe/Paris", "巴黎时间 (UTC+2)"),
        ("Europe/Berlin", "柏林时间 (UTC+2)"),
        ("Asia/Singapore", "新加坡时间 (UTC+8)"),
        ("Asia/Hong_Kong", "香港时间 (UTC+8)"),
        ("Australia/Sydney", "悉尼时间 (UTC+10)"),
    ]

    private var currentLanguageLabel: String {
        languages.first { $0.0 == locale.language }?.1 ?? "中文"
    }

    private var currentTimezoneLabel: String {
        timezones.first { $0.0 == locale.timezone }?.1 ?? "北京时间 (UTC+8)"
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)

                ScrollView {
                    VStack(spacing: 0) {
                        SettingsRow(
                            icon: "globe",
                            title: locale.loc("Language"),
                            value: currentLanguageLabel
                        ) {
                            LanguagePickerView(locale: locale, languages: languages)
                        }

                        Divider()
                            .background(Color.white.opacity(0.15))
                            .padding(.leading, 56)

                        SettingsRow(
                            icon: "clock",
                            title: locale.loc("Timezone"),
                            value: currentTimezoneLabel
                        ) {
                            TimezonePickerView(locale: locale, timezones: timezones)
                        }

                        Divider()
                            .background(Color.white.opacity(0.15))
                            .padding(.leading, 56)

                        Button {
                            isRefreshing = true
                            matchService.refreshCache()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                isRefreshing = false
                                dismiss()
                            }
                        } label: {
                            HStack(spacing: 12) {
                                ZStack {
                                    if isRefreshing {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    } else {
                                        Image(systemName: "arrow.clockwise")
                                            .font(.system(size: 16))
                                            .foregroundColor(.white)
                                            .frame(width: 24, height: 24)
                                    }
                                }

                                Text(locale.isChinese ? "刷新缓存" : "Refresh Cache")
                                    .foregroundColor(.white)

                                Spacer()
                            }
                            .padding(.vertical, 14)
                            .padding(.horizontal, 20)
                        }
                        .disabled(isRefreshing)
                    }
                    .background(Color.white.opacity(0.05))
                    .cornerRadius(12)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 20)
                }
            }
            .navigationTitle(locale.loc("Settings"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(locale.loc("Close")) {
                        dismiss()
                    }
                    .foregroundColor(.yellow)
                }
            }
        }
    }
}

struct SettingsRow<Destination: View>: View {
    let icon: String
    let title: String
    let value: String
    @ViewBuilder let destination: () -> Destination

    var body: some View {
        NavigationLink(destination: destination) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 16))
                    .foregroundColor(.white)
                    .frame(width: 24, height: 24)

                Text(title)
                    .foregroundColor(.white)

                Spacer()

                Text(value)
                    .foregroundColor(.secondary)

                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)
            }
            .padding(.vertical, 14)
            .padding(.horizontal, 20)
        }
    }
}

struct LanguagePickerView: View {
    let locale: AppLocale
    let languages: [(String, String)]

    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)

            VStack(spacing: 0) {
                ForEach(languages, id: \.0) { lang in
                    Button {
                        locale.language = lang.0
                    } label: {
                        HStack {
                            Text(lang.1)
                                .foregroundColor(.white)
                            Spacer()
                            if locale.language == lang.0 {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.yellow)
                            }
                        }
                        .padding(.vertical, 14)
                        .padding(.horizontal, 20)
                    }

                    if lang.0 != languages.last?.0 {
                        Divider()
                            .background(Color.white.opacity(0.15))
                            .padding(.leading, 20)
                    }
                }
            }
            .background(Color.white.opacity(0.05))
            .cornerRadius(12)
            .padding(.horizontal, 20)
        }
        .navigationTitle(locale.loc("Language"))
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct TimezonePickerView: View {
    let locale: AppLocale
    let timezones: [(String, String)]

    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)

            ScrollView {
                VStack(spacing: 0) {
                    ForEach(timezones, id: \.0) { tz in
                        Button {
                            locale.timezone = tz.0
                        } label: {
                            HStack {
                                Text(tz.1)
                                    .foregroundColor(.white)
                                Spacer()
                                if locale.timezone == tz.0 {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.yellow)
                                }
                            }
                            .padding(.vertical, 14)
                            .padding(.horizontal, 20)
                        }

                        if tz.0 != timezones.last?.0 {
                            Divider()
                                .background(Color.white.opacity(0.15))
                                .padding(.leading, 20)
                        }
                    }
                }
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)
                .padding(.horizontal, 20)
                .padding(.vertical, 20)
            }
        }
        .navigationTitle(locale.loc("Timezone"))
        .navigationBarTitleDisplayMode(.inline)
    }
}
