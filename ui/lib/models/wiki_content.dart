class WikiContent {
  final String? mainContent;
  final String? category;
  final List<WikiContent>? children;

  factory WikiContent.fromJson(String content, Map<String, dynamic> json) {
    final mainContent = json['main_content'];
    json.remove('main_content');
    return WikiContent(
      mainContent: mainContent,
      category: content,
      children: List<WikiContent>.of(
        json.entries
            .map((entry) => WikiContent.fromJson(entry.key, entry.value)),
      ),
    );
  }

  WikiContent({
    required this.mainContent,
    this.category,
    this.children,
  });

    @override
  bool operator ==(Object other) =>
      other is WikiContent &&
      other.runtimeType == runtimeType &&
      other.mainContent == mainContent && other.category ==other.category;

  @override
  int get hashCode => Object.hash(mainContent, category);
  
}
