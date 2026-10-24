// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Nursery';

  @override
  String get preview => 'Development foundation · synthetic preview';

  @override
  String get heading => 'A little closer, all day.';

  @override
  String get staffHeading => 'More time for little moments.';

  @override
  String get language => 'العربية';

  @override
  String get experience => 'Preview experience';

  @override
  String get parent => 'Parent';

  @override
  String get staff => 'Teacher';

  @override
  String get home => 'Home';

  @override
  String get timeline => 'Timeline';

  @override
  String get notices => 'Notices';

  @override
  String get empty =>
      'No operational records. Authentication and storage are not connected.';
}
