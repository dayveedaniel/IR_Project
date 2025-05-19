import 'package:flutter/material.dart';
import 'package:ui/models/document_model.dart';
import 'package:ui/state_noitifiers/list_tile_notifier.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  QueryResponse? queryResponse;
  final controller = TextEditingController();
  final notifier = ListTileNotifier()..getWikiContents(null);

  @override
  Widget build(BuildContext context) {
    return SelectionArea(
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: Text(
              'Information Retrival Category: Artificial Intelligence Wiki'),
          bottom: PreferredSize(
            preferredSize: Size.fromHeight(80),
            child: Padding(
              padding: EdgeInsets.only(bottom: 10),
              child: SearchBar(
                controller: controller,
                trailing: [
                  IconButton(
                    onPressed: () {
                      controller.clear();
                      notifier.getWikiContents(null);
                    },
                    icon: Icon(Icons.cancel),
                  )
                ],
                hintText: 'Search category or content',
                onSubmitted: (value) async {
                  notifier.pageContentFromApi(value);
                },
              ),
            ),
          ),
        ),
        body: ListenableBuilder(
          listenable: notifier,
          builder: (context, child) {
            return Padding(
              padding: const EdgeInsets.all(24.0),
              child: notifier.isLoading
                  ? Center(child: CircularProgressIndicator.adaptive())
                  : SingleChildScrollView(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (notifier.isSearchPage) ...[
                            Text(
                              'Generated search query',
                              style: TextStyle(fontSize: 20),
                            ),
                            SizedBox(height: 8),
                            Text(notifier.pageTitle ?? ''),
                            SizedBox(height: 12),
                            Text(
                              'Final answer',
                              style: TextStyle(fontSize: 20),
                            ),
                            SizedBox(height: 8),
                            Text(notifier.pageSubtitle ?? ''),
                          ] else
                            Row(
                              children: [
                                IconButton(
                                  onPressed: notifier.onBackTap,
                                  highlightColor: Theme.of(context)
                                      .colorScheme
                                      .secondaryContainer,
                                  icon: Icon(Icons.chevron_left),
                                ),
                                SizedBox(width: 16),
                                Text(
                                  "Path - ${notifier.routes.map((element) => element.title).join('/')}",
                                  style: TextStyle(fontSize: 20),
                                ),
                              ],
                            ),
                          SizedBox(height: 16),
                          Text(
                            "${notifier.pageContent?.length} Total Catergories",
                            style: TextStyle(fontSize: 20),
                          ),
                          const SizedBox(height: 16),
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Expanded(
                                flex: 3,
                                child: DataView(
                                  data: notifier.pageContent ?? [],
                                  onTap: (ListTileContent value) {
                                    notifier.onTileTap(value);
                                  },
                                ),
                              ),
                              if (notifier.routes.isNotEmpty) ...[
                                Container(
                                  color: Colors.grey,
                                  height:
                                      MediaQuery.sizeOf(context).height * 0.8,
                                  width: 4,
                                  margin: EdgeInsets.symmetric(horizontal: 24),
                                ),
                                Expanded(
                                  flex: 3,
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(
                                        notifier.routes.last.contentTitle,
                                        style: TextStyle(fontSize: 24),
                                      ),
                                      SizedBox(height: 16),
                                      Text(notifier.routes.last.contentBody),
                                    ],
                                  ),
                                ),
                              ]
                            ],
                          ),
                        ],
                      ),
                    ),
            );
          },
        ),
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

  final List<ListTileContent> data;
  final ValueSetter<ListTileContent> onTap;

  @override
  Widget build(BuildContext context) {
    return Column(
      spacing: 16,
      children: [
        for (final content in data)
          ListTile(
            trailing: Icon(Icons.chevron_right),
            subtitle: Text('Total subsections: ${content.subtitle}'),
            hoverColor: Theme.of(context)
                .colorScheme
                .secondaryContainer
                .withOpacity(0.2),
            tileColor: Theme.of(context).colorScheme.secondaryContainer,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(16)),
            ),
            onTap: () => onTap(content),
            title: Text(content.title),
          )
      ],
    );
  }
}
