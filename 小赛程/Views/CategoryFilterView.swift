import SwiftUI

struct CategoryFilterView: View {
    let categories: [GameCategory]
    @Binding var selectedCategory: GameCategory
    @Environment(AppLocale.self) var locale

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(categories) { category in
                    Button(action: {
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                            selectedCategory = category
                        }
                    }) {
                        VStack(spacing: 4) {
                            Image(systemName: category.icon)
                                .font(.body)
                                .foregroundColor(selectedCategory == category ? .white : .secondary)
                            Text(category.localizedName(locale))
                                .font(.caption2)
                                .foregroundColor(selectedCategory == category ? .white : .secondary)
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 8)
                        .background(selectedCategory == category ? Color(.systemBlue) : Color(.systemGray5))
                        .cornerRadius(12)
                        .scaleEffect(selectedCategory == category ? 1.05 : 1)
                        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: selectedCategory)
                    }
                }
            }
        }
    }
}
