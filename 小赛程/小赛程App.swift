import SwiftUI

@main
struct 小赛程App: App {
    @State private var locale = AppLocale.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(locale)
                .preferredColorScheme(.dark)
        }
    }
}
