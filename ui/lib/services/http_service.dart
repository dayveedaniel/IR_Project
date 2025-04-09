import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:ui/models/document_model.dart';

const localHost = 'localhost:8000';

class HttpService {
  Future<List<DocumentModel>> searchFiles(String query) async {
    var client = http.Client();
    try {
      var response = await client.get(
        Uri.http(localHost, '/search/', {'query': query}),
      );
      var decodedResponse = jsonDecode(utf8.decode(response.bodyBytes)) as Map;
      print(decodedResponse);
      print('RESULTS ${decodedResponse['results'][0]}');
      return (decodedResponse['results'] as List).map((json)=>DocumentModel.fromJson(json)).toList();
    } finally {
      // client.close();
    }
  }
}
