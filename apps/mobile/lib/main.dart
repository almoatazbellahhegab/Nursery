/// Public app foundation. No HTTP, identity, storage or care data is connected.
library;

import 'package:flutter/material.dart';

void main() => runApp(const NurseryApp());

/// Application entry point; domain policies belong in the API, not widgets.
class NurseryApp extends StatelessWidget {
  const NurseryApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Nursery',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff285947)),
          useMaterial3: true,
        ),
        home: const Scaffold(
          body: SafeArea(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Text('Nursery development foundation. No operational data.'),
            ),
          ),
        ),
      );
}
