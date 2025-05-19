import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:ui/models/document_model.dart';

/// Host address for the local search API endpoint.
const localHost = 'localhost:8000';

/// Service responsible for making HTTP requests to the search backend.
class HttpService {
  /// Sends a GET request to the search API with the given [query].
  ///
  /// Returns a [QueryResponse] parsed from the JSON response body.
  ///
  /// Throws an exception if the network request fails or if JSON decoding fails.
  Future<QueryResponse> searchFiles(String query) async {
    // Create a new HTTP client for the request
    final client = http.Client();

    try {
      // Build the URI: http://localhost:8000/search/?query=<query>
      final uri = Uri.http(
        localHost,
        '/search/',
        {'query': query},
      );

      // Execute the GET request
      final response = await client.get(uri);

      // Decode the response body as UTF-8 and parse JSON into a Map
      final decodedResponse = jsonDecode(
        utf8.decode(response.bodyBytes),
      ) as Map<String, dynamic>;

      // Convert the JSON map into a QueryResponse model object

      return QueryResponse.fromJson(decodedResponse);
    } finally {
      // Close the client to release resources
      client.close();
    }
  }
}

final map = {
  "user_question": "test",
  "generated_search_query": "test",
  "retrieved_context": [
    {
      "doc_id": "Minimum intelligent signal test||main_content",
      "semantic_similarity": 0.40890111196241813,
      "ngram_match_ratio": 0,
      "text_snippet": "{{Use dmy dates|date=December 2023}}\nThe '''minimum intelligent signal test''', or '''MIST''', is a variation of the [[Turing test]] proposed by [[Chris McKinstry]] in which only [[Wiktionary:boolean|boolean]] (yes/no or true/false) answers may be given to questions.  The purpose of such a test is to provide a quantitative statistical measure of ''humanness'', which may subsequently be used to optimize the performance of [[artificial intelligence]] systems intended to imitate human responses.\n\nMcKinstry gathered approximately 80,000 propositions that could be answered yes or no, e.g.:\n\n* Is Earth a planet?\n* Was Abraham Lincoln once President of the United States?\n* Is the sun bigger than my foot?\n* Do people sometimes lie?\n\nHe called these propositions [[Mindpixel]]s.\n\nThese questions test both specific knowledge of aspects of culture, and basic facts about the meaning of various words and concepts. It could therefore be compared with the [[SAT]], [[intelligence test]]ing and other controversial measures of mental ability. McKinstry's aim was not to distinguish between shades of intelligence but to identify whether a computer program could be considered intelligent at all.\n\nAccording to McKinstry, a program able to do much better than chance on a large number of MIST questions would be judged to have some level of intelligence and understanding. For example, on a 20-question test, if a program were guessing the answers at random, it could be expected to score 10 correct on average. But the [[probability]] of a program scoring 20 out of 20 correct by guesswork is only one in 2<sup>20</sup>, i.e. one in 1,048,576; so if a program were able to sustain this level of performance over several independent trials, with no prior access to the propositions, it should be considered intelligent."
    },
    {
      "doc_id": "Artificial general intelligence||== Characteristics ==||===Tests for human-level AGI{{Anchor|Tests_for_confirming_human-level_AGI}}===||main_content",
      "semantic_similarity": 0.40456976080571644,
      "ngram_match_ratio": 0,      "text_snippet": "Several tests meant to confirm human-level AGI have been considered, including:\n\n;[[Turing test|The Turing Test]] ([[Alan Turing|''Turing'']])  \n:[[File:Weakness of Turing test 1.svg|thumb|The Turing test can provide some evidence of intelligence, but it penalizes non-human intelligent behavior and may incentivize [[artificial stupidity]].]]Proposed by Alan Turing in his 1950 paper \"Computing Machinery and Intelligence,\" this test involves a human judge engaging in natural language conversations with both a human and a machine designed to generate human-like responses. The machine passes the test if it can convince the judge it is human a significant fraction of the time. Turing proposed this as a practical measure of machine intelligence, focusing on the ability to produce human-like responses rather than on the internal workings of the machine.{{Sfn|Turing|1950}}\n\n: Turing described the test as follows:\n{{Quote|text=The idea of the test is that the machine has to try and pretend to be a man, by answering questions put to it, and it will only pass if the pretence is reasonably convincing. A considerable portion of a jury, who should not be expert about machines, must be taken in by the pretence.}}\n\n: In 2014, a chatbot named [[Eugene Goostman]], designed to imitate a 13-year-old Ukrainian boy, reportedly passed a Turing Test event by convincing 33% of judges that it was human. However, this claim was met with significant skepticism from the AI research community, who questioned the test's implementation and its relevance to AGI.\n\n: More recently, a 2024 study suggested that [[GPT-4]] was identified as human 54% of the time in a randomized, controlled version of the Turing Test—surpassing older chatbots like ELIZA while still falling behind actual humans (67%). \n\n;The Robot College Student Test ([[Ben Goertzel|''Goertzel'']])  \n: A machine enrolls in a university, taking and passing the same classes that humans would, and obtaining a degree. LLMs can now pass university degree-level exams without even attending the classes.\n\n;The Employment Test ([[Nils John Nilsson|''Nilsson'']])  \n: A machine performs an economically important job at least as well as humans in the same job. AIs are now replacing humans in many roles as varied as fast food and marketing.\n\n;The Ikea test ([[Gary Marcus|''Marcus'']])  \n: Also known as the Flat Pack Furniture Test. An AI views the parts and instructions of an Ikea flat-pack product, then controls a robot to assemble the furniture correctly.\n\n;The Coffee Test ([[Steve Wozniak|''Wozniak'']])  \n: A machine is required to enter an average American home and figure out how to make coffee: find the coffee machine, find the coffee, add water, find a mug, and brew the coffee by pushing the proper buttons. This has not yet been completed.\n\n;The Modern Turing Test (''[[Mustafa Suleyman|Suleyman]]'')  \n: An AI model is given \$100,000 and has to obtain \$1&nbsp;million."
      },
    {
      "doc_id": "Reverse Turing test||main_content",
      "semantic_similarity": 0.4015075976855115,
      "ngram_match_ratio": 0,
      "text_snippet": "{{Short description|Turing test in which the objective or roles between computers and humans have been reversed}}\n{{multiple issues|\n{{More footnotes|date=August 2009}}\n{{Original research|date=August 2009}}\n}}\n\nA '''reverse Turing test''' is a [[Turing test]] in which failure suggests that the test-taker is human, while success suggests the test-taker is automated. \n\nConventionally, the Turing test is conceived as having a human judge and a computer subject which attempts to appear human."
    }
  ],  "final_answer": "Based on the provided documents, several tests have been considered to assess intelligence, including:\n\n*   **The Turing Test:** This test, originally proposed by Alan Turing, involves a human judge engaging in natural language conversations with both a human and a machine. A machine passes if it can convince the judge it is human.\n*   **The Reverse Turing Test:** In this test, failure suggests the test-taker is human, while success suggests the test-taker is automated."
};
