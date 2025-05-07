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
