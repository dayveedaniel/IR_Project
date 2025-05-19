import 'package:flutter/material.dart';
import 'package:ui/models/wiki_content.dart';
import 'package:ui/services/http_service.dart';
import 'package:ui/services/json_parser.dart';

class ListTileNotifier extends ChangeNotifier {
  bool _isLoading = false;
  bool _isSearchPage = false;
  String? _pageTitle;
  String? _pageSubtitle;
  List<ListTileContent>? _pageContent;
  Set<ListTileContent> routes = {};

  bool get isLoading => _isLoading;
  bool get isSearchPage => _isSearchPage;
  List<ListTileContent>? get pageContent => _pageContent;
  String? get pageTitle => _pageTitle;
  String? get pageSubtitle => _pageSubtitle;

  void setIsLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void getWikiContents(List<WikiContent>? contentChildren) async {
    _isSearchPage = false;
    final contents = contentChildren ?? await JsonParserService().getContents();
    _pageContent = contents
        .map((e) => ListTileContent(
              title: e.category ?? '',
              subtitle: 'Total Subscetions: ${e.children?.length}',
              contentBody: e.mainContent ?? '',
              contentTitle: e.category ?? '',
              contentSubtitle: null,
              children: e.children,
            ))
        .toList();
    notifyListeners();
  }

  void pageContentFromApi(String text) async {
    final response = await HttpService().searchFiles(text);
    _isSearchPage = true;
    _pageTitle = response.generatedSearchQuery;
    _pageSubtitle = response.finalAnswer;

    _pageContent = response.retrievedContext
        .map((e) => ListTileContent(
              title: e.docId,
              subtitle:
                  'N-gram Match Ratio : ${e.ngramMatchRatio} Semantic Similarity ${e.semanticSimilarity}',
              contentBody: e.textSnippet,
              contentTitle: '',
              contentSubtitle: '',
              children: [],
            ))
        .toList();
    notifyListeners();
  }

  void onTileTap(ListTileContent content) {
    if (_isSearchPage) {
      return;
    }
    // if (routes.isNotEmpty && (routes.last.children?.isEmpty ?? false)) {
    //   routes.remove(routes.last);
    // }
    routes.add(content);
    if (content.children != null) getWikiContents(content.children);
    notifyListeners();
  }

  void onBackTap() {
    routes.remove(routes.last);
    notifyListeners();
  }
}

class ListTileContent {
  final String title;
  final String subtitle;
  final String contentBody;
  final String contentTitle;
  final String? contentSubtitle;
  final List<WikiContent>? children;

  ListTileContent({
    required this.title,
    required this.subtitle,
    required this.contentBody,
    required this.contentTitle,
    required this.contentSubtitle,
    required this.children,
  });
}
