import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:ui/models/document_model.dart';

const localHost = 'localhost:8000';

class HttpService {
  Future<QueryResponse> searchFiles(String query) async {
    var client = http.Client();
    try {
      var response = await client.get(
        Uri.http(localHost, '/search/', {'query': query}),
      );
      Map<String, dynamic> decodedResponse = jsonDecode(utf8.decode(response.bodyBytes));
      return QueryResponse.fromJson(decodedResponse);
    } finally {
      // client.close();
    }
  }
}
