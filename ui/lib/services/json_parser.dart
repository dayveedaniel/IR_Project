import 'dart:convert';
// import 'package:flutter/services.dart';
import 'dart:io';

import 'package:ui/models/wiki_content.dart';

class JsonParserService {
  Future<Map<String,dynamic>> readJsonFile() async {
    var input = await File(
            '/Users/dayveed/VscodeProjects/IR_Project/data_mining/data.json')
        .readAsString();
    var map = jsonDecode(input) as List;
    return map.first;
  }

  Future<List<WikiContent>> getContents() async {
    final list = await readJsonFile();
    return List<WikiContent>.of(
        list.entries.map((entry) => WikiContent.fromJson(entry.key,entry.value)));
  }
}
