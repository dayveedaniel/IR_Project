class DocumentModel {
  final String docID;
  final double semantic_similarity;
  final double ngram_match_ratio;
  final String text_snippet;

  DocumentModel(
      {required this.docID,
      required this.semantic_similarity,
      required this.ngram_match_ratio,
      required this.text_snippet,});

  factory DocumentModel.fromJson(Map<String, dynamic> json) {
    return DocumentModel(
      docID: json['doc_id'],
      semantic_similarity: json['semantic_similarity'],
      ngram_match_ratio: json['ngram_match_ratio'].toDouble(),
      text_snippet: json['text_snippet'],
    );
  }
}
