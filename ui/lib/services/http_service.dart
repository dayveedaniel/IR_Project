import 'dart:convert';

import 'package:http/http.dart' as http;

const localHost = 'localhost:8000';

class HttpService {
  void searchFiles(String query) async {
    var client = http.Client();
    try {
      var response = await client.get(
        Uri.http(localHost, '/search/', {'query': query}),
      );
      var decodedResponse = jsonDecode(utf8.decode(response.bodyBytes)) as Map;
      print(decodedResponse);
      print('decodedResponse $decodedResponse');
    } finally {
      // client.close();
    }
  }
}
