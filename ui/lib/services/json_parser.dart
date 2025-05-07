import 'dart:convert';
import 'dart:io';

import 'package:ui/models/wiki_content.dart';

/// Service for parsing JSON files and converting data into [WikiContent] objects.
class JsonParserService {
  /// Reads the JSON file from disk and returns the first object as a Map.
  ///
  /// The file path is hardcoded and points to the local data.json file.
  /// Throws an exception if the file cannot be read or if JSON decoding fails.
  Future<Map<String, dynamic>> readJsonFile() async {
    // Read the file contents as a string
    final input = await File(
      '/Users/dayveed/VscodeProjects/IR_Project/data_mining/data.json',
    ).readAsString();

    // Decode the JSON string into a List
    final map = jsonDecode(input) as List;

    // Return the first JSON object in the list
    return map.first as Map<String, dynamic>;
  }

  /// Retrieves a list of [WikiContent] instances parsed from the JSON file.
  ///
  /// Reads the JSON map via [readJsonFile()], then converts each entry into
  /// a [WikiContent] object using its factory constructor.
  Future<List<WikiContent>> getContents() async {
    // Read raw JSON data as a Map
    final jsonMap = await readJsonFile();

    // Convert each key/value pair in the map to a WikiContent object
    return jsonMap.entries
        .map(
          (entry) => WikiContent.fromJson(
            entry.key,
            entry.value,
          ),
        )
        .toList();
  }
}
