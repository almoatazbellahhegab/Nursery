/// Public app foundation. No HTTP, identity, storage or care data is connected.
library;

import 'package:flutter/material.dart';
import 'l10n/app_localizations.dart';

void main() => runApp(const NurseryApp());

/// Application entry point; domain policies belong in the API, not widgets.
class NurseryApp extends StatefulWidget {
  const NurseryApp({super.key});

  @override
  State<NurseryApp> createState() => _NurseryAppState();
}

class _NurseryAppState extends State<NurseryApp> {
  Locale _locale = const Locale('en');

  @override
  Widget build(BuildContext context) => MaterialApp(
    onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,
    locale: _locale,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff285947)),
      useMaterial3: true,
    ),
    home: FoundationShell(
      onLanguageChanged: () => setState(() {
        _locale = Locale(_locale.languageCode == 'en' ? 'ar' : 'en');
      }),
    ),
  );
}

/// Presentation state only. A selected experience never grants a server role.
class FoundationShell extends StatefulWidget {
  const FoundationShell({required this.onLanguageChanged, super.key});

  final VoidCallback onLanguageChanged;

  @override
  State<FoundationShell> createState() => _FoundationShellState();
}

class _FoundationShellState extends State<FoundationShell> {
  int _tab = 0;
  bool _staff = false;

  @override
  Widget build(BuildContext context) {
    final text = AppLocalizations.of(context)!;
    final titles = [text.home, text.timeline, text.notices];
    return Scaffold(
      appBar: AppBar(
        title: Text(text.appTitle),
        actions: [
          TextButton(
            onPressed: widget.onLanguageChanged,
            child: Text(text.language),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsetsDirectional.all(24),
          children: [
            Text(text.preview),
            const SizedBox(height: 24),
            DropdownButtonFormField<bool>(
              initialValue: _staff,
              decoration: InputDecoration(labelText: text.experience),
              items: [
                DropdownMenuItem(value: false, child: Text(text.parent)),
                DropdownMenuItem(value: true, child: Text(text.staff)),
              ],
              onChanged: (value) => setState(() => _staff = value ?? false),
            ),
            const SizedBox(height: 32),
            Text(
              _staff ? text.staffHeading : text.heading,
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            const SizedBox(height: 24),
            Text(titles[_tab], style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            Text(text.empty),
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (value) => setState(() => _tab = value),
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.home_outlined),
            label: text.home,
          ),
          NavigationDestination(
            icon: const Icon(Icons.schedule),
            label: text.timeline,
          ),
          NavigationDestination(
            icon: const Icon(Icons.notifications_outlined),
            label: text.notices,
          ),
        ],
      ),
    );
  }
}
