
class RetrievedContext {
    final String docId;
    final double semanticSimilarity;
    final int ngramMatchRatio;
    final String textSnippet;

    RetrievedContext({
        required this.docId,
        required this.semanticSimilarity,
        required this.ngramMatchRatio,
        required this.textSnippet,
    });

    factory RetrievedContext.fromJson(Map<String, dynamic> json) => RetrievedContext(
        docId: json["doc_id"],
        semanticSimilarity: json["semantic_similarity"]?.toDouble(),
        ngramMatchRatio: json["ngram_match_ratio"],
        textSnippet: json["text_snippet"],
    );
}

class QueryResponse {
    final String generatedSearchQuery;
    final String userQuestion;
    final String finalAnswer;
    final List<RetrievedContext> retrievedContext;
    

    QueryResponse({
        required this.userQuestion,
        required this.generatedSearchQuery,
        required this.retrievedContext,
        required this.finalAnswer,
    });

    factory QueryResponse.fromJson(Map<String, dynamic> json) => QueryResponse(
        userQuestion: json["user_question"],
        generatedSearchQuery: json["generated_search_query"],
        retrievedContext: List<RetrievedContext>.from(json["retrieved_context"].map((x) => RetrievedContext.fromJson(x))),
        finalAnswer: json["final_answer"],
    );
}