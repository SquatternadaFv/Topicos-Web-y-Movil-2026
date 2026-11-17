import 'package:flutter/material.dart';
import 'data/api_client.dart';
import 'screens/catalog_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/order_screen.dart';
import 'screens/chat_screen.dart';
import 'widgets/common.dart';

void main() => runApp(const OpticaApp());

class OpticaApp extends StatelessWidget {
  final ApiClient? api;
  const OpticaApp({super.key, this.api});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Lúmina · Óptica',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: cream,
      colorScheme: ColorScheme.fromSeed(
        seedColor: ink,
        primary: ink,
        secondary: accent,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: cream,
        foregroundColor: ink,
        centerTitle: false,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 19),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
    ),
    home: HomeScreen(api: api),
  );
}

class HomeScreen extends StatefulWidget {
  final ApiClient? api;
  const HomeScreen({super.key, this.api});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final api = widget.api ?? ApiClient();
  int selected = 0;
  @override
  void dispose() {
    api.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Row(
        children: [
          Icon(Icons.blur_circular, size: 30),
          SizedBox(width: 10),
          Text(
            'lúmina',
            style: TextStyle(fontWeight: FontWeight.w700, letterSpacing: -1),
          ),
        ],
      ),
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 20),
          child: Center(
            child: Text(
              'ÓPTICA / P1 + P2',
              style: Theme.of(context).textTheme.labelSmall,
            ),
          ),
        ),
      ],
    ),
    body: IndexedStack(
      index: selected,
      children: [
        CatalogScreen(
          api: api,
          onRecommend: () => setState(() => selected = 1),
        ),
        ProfileScreen(api: api),
        OrderLookupScreen(api: api),
        ChatScreen(api: api, onRecommend: () => setState(() => selected = 1)),
      ],
    ),
    bottomNavigationBar: NavigationBar(
      selectedIndex: selected,
      onDestinationSelected: (i) => setState(() => selected = i),
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.grid_view_outlined),
          selectedIcon: Icon(Icons.grid_view_rounded),
          label: 'Catálogo',
        ),
        NavigationDestination(
          icon: Icon(Icons.auto_awesome_outlined),
          selectedIcon: Icon(Icons.auto_awesome),
          label: 'Mi recomendación',
        ),
        NavigationDestination(
          icon: Icon(Icons.receipt_long_outlined),
          label: 'Consultar folio',
        ),
        NavigationDestination(
          icon: Icon(Icons.chat_bubble_outline),
          selectedIcon: Icon(Icons.chat_bubble),
          label: 'Asistente',
        ),
      ],
    ),
  );
}
