import 'package:flutter/material.dart';
import 'package:ui/models/wiki_content.dart';
import 'package:ui/services/json_parser.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Set<WikiContent> routes = {};

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title:
            Text('Information Retrival Category: Artificial Intelligence Wiki'),
        bottom: PreferredSize(
          preferredSize: Size.fromHeight(80),
          child: Padding(
            padding: EdgeInsets.only(bottom: 10),
            child: SearchBar(
              hintText: 'Search category or content',
            ),
          ),
        ),
      ),
      body: FutureBuilder<List<WikiContent>>(
        future: JsonParserService().getContents(),
        builder: (context, snapshot) {
          final data = routes.isNotEmpty &&
                  routes.last.children != null &&
                  routes.last.children!.isNotEmpty
              ? routes.last.children!
              : snapshot.data ?? [];
          return snapshot.hasData
              ? Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          IconButton(
                            onPressed: () {
                              setState(() {
                                routes.remove(routes.last);
                              });
                            },
                            highlightColor: Theme.of(context)
                                .colorScheme
                                .secondaryContainer,
                            icon: Icon(Icons.chevron_left),
                          ),
                          SizedBox(width: 16),
                          Text(
                            "Path - ${routes.map((element) => element.category ?? '').join('/')}",
                            style: TextStyle(fontSize: 20),
                          ),
                        ],
                      ),
                      Text(
                        "${data.length} Total Catergories",
                        style: TextStyle(fontSize: 20),
                      ),
                      const SizedBox(height: 16),
                      Expanded(
                        child: Row(
                          children: [
                            Expanded(
                              flex: 2,
                              child: DataView(
                                data: data,
                                onTap: (WikiContent value) {
                                  setState(() {
                                    if (routes.isNotEmpty && (routes.last.children?.isEmpty ??
                                        false)) {
                                      routes.remove(routes.last);
                                    }
                                    routes.add(value);
                                  });
                                  print('len ${routes.length}');
                                },
                              ),
                            ),
                            if (routes.isNotEmpty) ...[
                              Container(
                                color: Colors.grey,
                                height: double.maxFinite,
                                width: 4,
                                margin: EdgeInsets.symmetric(horizontal: 24),
                              ),
                              Expanded(
                                flex: 3,
                                child: ContentView(content: routes.last),
                              ),
                            ]
                          ],
                        ),
                      ),
                    ],
                  ),
                )
              : CircularProgressIndicator.adaptive();
        },
      ),
    );
  }
}

class DataView extends StatelessWidget {
  const DataView({
    super.key,
    required this.data,
    required this.onTap,
  });

  final List<WikiContent> data;
  final ValueSetter<WikiContent> onTap;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      separatorBuilder: (context, index) => SizedBox(height: 16),
      itemCount: data.length,
      itemBuilder: (context, index) {
        final wikiContent = data[index];
        return ListTile(
          trailing: Icon(Icons.chevron_right),
          subtitle: Text('Total subsections: ${wikiContent.children?.length}'),
          hoverColor:
              Theme.of(context).colorScheme.secondaryContainer.withOpacity(0.2),
          tileColor: Theme.of(context).colorScheme.secondaryContainer,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(16)),
          ),
          onTap: () => onTap(wikiContent),
          title: Text(wikiContent.category ?? ''),
        );
      },
    );
  }
}

class ContentView extends StatelessWidget {
  const ContentView({
    super.key,
    required this.content,
  });

  final WikiContent content;
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          content.category ?? '',
          style: TextStyle(fontSize: 24),
        ),
        SizedBox(height: 16),
        Expanded(
          child: SingleChildScrollView(
            child: Text(content.mainContent ?? 'No Content available'),
          ),
        ),
      ],
    );
  }
}
