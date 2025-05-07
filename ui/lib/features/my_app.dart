import 'package:flutter/material.dart';
import 'package:ui/features/home_page.dart';

/// The root widget of the application.
///
/// Sets up the [MaterialApp] with a title, theme, and the home page.
class MyApp extends StatelessWidget {
  /// Creates a constant instance of [MyApp].
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Wraps the entire app in a Material design environment.
    return MaterialApp(
      // Title used by the device to identify the app (e.g., in app switcher).
      title: 'Information Retrieval',

      // Defines the visual theme for the app using Material 3 and a seeded color.
      theme: ThemeData(
        // Generates a color scheme from a single seed color.
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
        ),
        // Enables Material 3 design components and styling.
        useMaterial3: true,
      ),

      // Sets the initial route / home screen of the app.
      home: const MyHomePage(),
    );
  }
}
