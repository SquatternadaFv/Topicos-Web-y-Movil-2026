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
      fontFamily: 'LuminaSans',
      useMaterial3: true,
      scaffoldBackgroundColor: cream,
      colorScheme: ColorScheme.fromSeed(
        seedColor: ink,
        primary: ink,
        secondary: accent,
        surface: cream,
      ),
      textTheme: const TextTheme(
        bodyMedium: TextStyle(color: ink, fontSize: 14, height: 1.5),
        bodyLarge: TextStyle(color: ink, fontSize: 16, height: 1.5),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: cream,
        foregroundColor: ink,
        centerTitle: false,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 20,
        ),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: line),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: ink, width: 1.5),
        ),
      ),
      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: cream,
        indicatorColor: accent,
        surfaceTintColor: Colors.transparent,
      ),
      dividerTheme: const DividerThemeData(color: line, thickness: 1),
      chipTheme: ChipThemeData(
        backgroundColor: lilac,
        side: BorderSide.none,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 19),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
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

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  late final api = widget.api ?? ApiClient();
  late final tabs = TabController(length: 4, vsync: this);
  int selected = 0;
  void select(int index) {
    tabs.animateTo(index);
    setState(() => selected = index);
  }

  @override
  void dispose() {
    api.dispose();
    tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final desktop = MediaQuery.sizeOf(context).width >= 1000;
    return Scaffold(
      appBar: AppBar(
        toolbarHeight: desktop ? 88 : 68,
        titleSpacing: desktop ? 48 : 22,
        title: const FittedBox(
          fit: BoxFit.scaleDown,
          alignment: Alignment.centerLeft,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.blur_on_rounded, size: 30),
              SizedBox(width: 10),
              Text(
                'lúmina',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.w500,
                  letterSpacing: -1.8,
                ),
              ),
            ],
          ),
        ),
        actions: [
          if (desktop)
            SizedBox(
              width: 570,
              child: TabBar(
                controller: tabs,
                onTap: select,
                labelColor: ink,
                unselectedLabelColor: muted,
                indicatorColor: ink,
                dividerColor: Colors.transparent,
                labelPadding: const EdgeInsets.symmetric(horizontal: 8),
                tabs: const [
                  Tab(text: 'Catálogo'),
                  Tab(text: 'Mi recomendación'),
                  Tab(text: 'Consultar folio'),
                  Tab(text: 'Asistente'),
                ],
              ),
            ),
          Padding(
            padding: EdgeInsets.only(right: desktop ? 48 : 22, left: 24),
            child: Center(
              child: Text(
                'ÓPTICA',
                style: const TextStyle(
                  fontSize: 10,
                  letterSpacing: 2.5,
                  color: muted,
                ),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          const Divider(height: 1),
          Expanded(
            child: IndexedStack(
              index: selected,
              children: [
                CatalogScreen(api: api, onRecommend: () => select(1)),
                ProfileScreen(api: api),
                OrderLookupScreen(api: api),
                ChatScreen(api: api, onRecommend: () => select(1)),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: desktop
          ? null
          : NavigationBar(
              selectedIndex: selected,
              onDestinationSelected: select,
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
}
