import SwiftUI

struct SearchBarView: View {
    @Binding var searchText: String
    @Environment(AppLocale.self) var locale

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
                .padding(.leading, 16)

            TextField(locale.loc("SearchPlaceholder"), text: $searchText)
                .foregroundColor(.white)

            if !searchText.isEmpty {
                Button(action: {
                    searchText = ""
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                        .padding(.trailing, 16)
                }
            }
        }
        .frame(height: 44)
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}
