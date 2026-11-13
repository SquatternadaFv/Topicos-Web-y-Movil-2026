import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class LaboratorioApp extends StatelessWidget {
  const LaboratorioApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Prácticas de Flutter',
    theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
    home: const Inicio(),
  );
}

class Inicio extends StatefulWidget {
  const Inicio({super.key});
  @override
  State<Inicio> createState() => _InicioState();
}

class _InicioState extends State<Inicio> {
  int pagina = 0;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Prácticas · widgets y API')),
    drawer: Drawer(
      child: SafeArea(
        child: Column(
          children: [
            const DrawerHeader(child: Text('Laboratorio de clase')),
            ListTile(
              title: const Text('Galería'),
              onTap: () {
                setState(() => pagina = 0);
                Navigator.pop(context);
              },
            ),
            ListTile(
              title: const Text('Consumo HTTP'),
              onTap: () {
                setState(() => pagina = 1);
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    ),
    body: SafeArea(
      child: IndexedStack(
        index: pagina,
        children: const [Galeria(), PantallaApi()],
      ),
    ),
    bottomNavigationBar: BottomNavigationBar(
      currentIndex: pagina,
      onTap: (v) => setState(() => pagina = v),
      items: const [
        BottomNavigationBarItem(icon: Icon(Icons.widgets), label: 'Widgets'),
        BottomNavigationBarItem(icon: Icon(Icons.http), label: 'API y chat'),
      ],
    ),
  );
}

class FolioTexto extends StatelessWidget {
  const FolioTexto(this.folio, {super.key});
  final String folio;
  @override
  Widget build(BuildContext context) => Text('Folio: $folio');
}

class Galeria extends StatefulWidget {
  const Galeria({super.key});
  @override
  State<Galeria> createState() => _GaleriaState();
}

class _GaleriaState extends State<Galeria> {
  int contador = 0;
  bool urgente = false, cargando = false;
  String medio = 'moto', filtro = '';
  final folios = ['DEMO-101', 'DEMO-102', 'DEMO-103'];
  late Future<String> resumen;
  @override
  void initState() {
    super.initState();
    resumen = cargar();
  }

  Future<String> cargar() async {
    await Future<void>.delayed(const Duration(milliseconds: 400));
    return '3 pedidos de demostración';
  }

  Future<void> actualizar() async {
    final n = cargar();
    setState(() => resumen = n);
    await n;
  }

  @override
  Widget build(BuildContext context) => DefaultTabController(
    length: 2,
    child: Column(
      children: [
        const TabBar(
          tabs: [
            Tab(text: 'Controles'),
            Tab(text: 'Listas y estado'),
          ],
        ),
        Expanded(
          child: TabBarView(
            children: [
              SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Galería reproducible',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const Text(
                      'Los folios DEMO son datos ilustrativos; esta pantalla no crea pedidos.',
                    ),
                    const SizedBox(height: 16),
                    const FolioTexto('DEMO-101'),
                    Text('Contador con estado: $contador'),
                    FilledButton(
                      onPressed: () => setState(() => contador++),
                      child: const Text('Sumar'),
                    ),
                    const Row(
                      children: [
                        Expanded(
                          child: Text(
                            'Folio largo con Expanded ocupa el espacio disponible',
                          ),
                        ),
                        Text('moto'),
                      ],
                    ),
                    SwitchListTile(
                      title: const Text('Envío urgente'),
                      value: urgente,
                      onChanged: (v) => setState(() => urgente = v),
                    ),
                    DropdownButton<String>(
                      value: medio,
                      items: const ['moto', 'bicicleta', 'camioneta', 'dron']
                          .map(
                            (m) => DropdownMenuItem(value: m, child: Text(m)),
                          )
                          .toList(),
                      onChanged: (v) => setState(() => medio = v!),
                    ),
                    FilledButton(
                      onPressed: () async {
                        final si = await showDialog<bool>(
                          context: context,
                          builder: (c) => AlertDialog(
                            title: const Text('Confirmar demostración'),
                            content: const Text(
                              'Esto no registra un pedido en el servidor.',
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(c, false),
                                child: const Text('Cancelar'),
                              ),
                              TextButton(
                                onPressed: () => Navigator.pop(c, true),
                                child: const Text('Sí'),
                              ),
                            ],
                          ),
                        );
                        if (!context.mounted) return;
                        if (si == true) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Confirmación local')),
                          );
                        }
                      },
                      child: const Text('Abrir AlertDialog'),
                    ),
                    FilledButton(
                      onPressed: cargando
                          ? null
                          : () async {
                              setState(() => cargando = true);
                              await Future<void>.delayed(
                                const Duration(milliseconds: 600),
                              );
                              if (mounted) setState(() => cargando = false);
                            },
                      child: const Text('Simular carga'),
                    ),
                    if (cargando) const CircularProgressIndicator(),
                    Card(
                      child: ListTile(
                        leading: const Icon(Icons.local_shipping),
                        title: const Text('Pedido de demostración'),
                        subtitle: const Text('DEMO-101'),
                        trailing: IconButton(
                          icon: const Icon(Icons.arrow_forward),
                          onPressed: () => Navigator.push(
                            context,
                            MaterialPageRoute<void>(
                              builder: (_) => const Detalle('DEMO-101'),
                            ),
                          ),
                        ),
                      ),
                    ),
                    GridView.count(
                      crossAxisCount: 3,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      children: const [
                        Card(child: Center(child: Text('Bici'))),
                        Card(child: Center(child: Text('Moto'))),
                        Card(child: Center(child: Text('Van'))),
                      ],
                    ),
                    Image.network(
                      'https://flutter.github.io/assets-for-api-docs/assets/widgets/owl.jpg',
                      height: 100,
                      errorBuilder: (_, _, _) => const Text(
                        'Imagen de red no disponible; la aplicación sigue funcionando',
                      ),
                    ),
                  ],
                ),
              ),
              RefreshIndicator(
                onRefresh: actualizar,
                child: ListView(
                  padding: const EdgeInsets.all(24),
                  children: [
                    TextField(
                      decoration: const InputDecoration(
                        labelText: 'Buscar folio',
                      ),
                      onChanged: (v) => setState(() => filtro = v),
                    ),
                    FutureBuilder<String>(
                      future: resumen,
                      builder: (context, s) {
                        if (s.hasError) return const Text('Error al cargar');
                        if (!s.hasData) return const LinearProgressIndicator();
                        return Text(s.data!);
                      },
                    ),
                    if (folios
                        .where((f) => f.contains(filtro.toUpperCase()))
                        .isEmpty)
                      const Text('No hay coincidencias'),
                    ...folios
                        .where((f) => f.contains(filtro.toUpperCase()))
                        .map(
                          (f) => ListTile(
                            title: Text(f),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () => Navigator.push(
                              context,
                              MaterialPageRoute<void>(
                                builder: (_) => Detalle(f),
                              ),
                            ),
                          ),
                        ),
                    FloatingActionButton.small(
                      heroTag: 'actualizar',
                      onPressed: actualizar,
                      child: const Icon(Icons.refresh),
                    ),
                    const Text(
                      'Tira hacia abajo para actualizar. Volver del detalle conserva el estado.',
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class Detalle extends StatelessWidget {
  const Detalle(this.folio, {super.key});
  final String folio;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(folio)),
    body: const Center(child: Text('Detalle local de demostración')),
  );
}

class PantallaApi extends StatefulWidget {
  const PantallaApi({super.key});
  @override
  State<PantallaApi> createState() => _PantallaApiState();
}

class _PantallaApiState extends State<PantallaApi> {
  static const base = String.fromEnvironment(
    'API_BASE',
    defaultValue: 'http://127.0.0.1:8000',
  );
  final form = GlobalKey<FormState>();
  final distancia = TextEditingController(text: '12.64'),
      peso = TextEditingController(text: '0.31'),
      hora = TextEditingController(text: '3'),
      mensaje = TextEditingController();
  String modelo = 'arbol', resultado = 'Aún no se ha llamado a la API.';
  bool esperando = false;
  final conversacion = <String>[];
  @override
  void dispose() {
    distancia.dispose();
    peso.dispose();
    hora.dispose();
    mensaje.dispose();
    super.dispose();
  }

  Future<void> llamar(
    String ruta,
    Map<String, dynamic> datos, {
    bool chat = false,
  }) async {
    setState(() => esperando = true);
    try {
      final r = await http
          .post(
            Uri.parse('$base$ruta'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(datos),
          )
          .timeout(const Duration(seconds: 10));
      final dynamic cuerpo = jsonDecode(r.body);
      if (!mounted) return;
      setState(() {
        resultado =
            'HTTP ${r.statusCode}\n${const JsonEncoder.withIndent('  ').convert(cuerpo)}';
        if (chat) {
          conversacion.add(
            'Asistente: ${cuerpo['respuesta'] ?? cuerpo['error']}',
          );
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        resultado = 'No se pudo consultar la API: $e';
        if (chat) {
          conversacion.add('Error de red; no se inventó una respuesta.');
        }
      });
    } finally {
      if (mounted) setState(() => esperando = false);
    }
  }

  String? numero(String? s) {
    final n = double.tryParse(s ?? '');
    return n == null || !n.isFinite || n < 0
        ? 'Número no negativo requerido'
        : null;
  }

  @override
  Widget build(BuildContext context) => SingleChildScrollView(
    padding: const EdgeInsets.all(24),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Consumo real de JSON',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const Text(
          'Servidor: $base · configurable con --dart-define=API_BASE=...',
        ),
        const Text(
          'Los demás campos del paquete de clase quedan fijos. El modelo y las reglas permanecen en el backend.',
        ),
        Form(
          key: form,
          child: Column(
            children: [
              TextFormField(
                controller: distancia,
                decoration: const InputDecoration(labelText: 'Distancia km'),
                keyboardType: TextInputType.number,
                validator: numero,
              ),
              TextFormField(
                controller: peso,
                decoration: const InputDecoration(labelText: 'Peso kg'),
                keyboardType: TextInputType.number,
                validator: (v) =>
                    numero(v) ??
                    (double.parse(v!) == 0 ? 'Mayor que cero requerido' : null),
              ),
              TextFormField(
                controller: hora,
                decoration: const InputDecoration(labelText: 'Hora 0–23'),
                keyboardType: TextInputType.number,
                validator: (v) {
                  final n = int.tryParse(v ?? '');
                  return n == null || n < 0 || n > 23
                      ? 'Hora entera 0–23'
                      : null;
                },
              ),
              DropdownButtonFormField<String>(
                initialValue: modelo,
                items: const ['arbol', 'bosque', 'red']
                    .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                    .toList(),
                onChanged: (v) => modelo = v!,
              ),
              FilledButton(
                onPressed: esperando
                    ? null
                    : () {
                        if (form.currentState!.validate()) {
                          llamar('/entregas/recomendar/', {
                            'modelo': modelo,
                            'distancia_km': double.parse(distancia.text),
                            'peso_kg': double.parse(peso.text),
                            'hora_salida': int.parse(hora.text),
                            'largo_cm': 11.7,
                            'ancho_cm': 7.6,
                            'alto_cm': 10.6,
                            'volumen_l': .94,
                            'fragil': 0,
                            'refrigerado': 0,
                            'valor_declarado_mxn': 4603,
                            'prioridad': 'mismo_dia',
                            'zona_destino': 'periferia',
                            'clima': 'despejado',
                            'trafico': 'medio',
                          });
                        }
                      },
                child: const Text('Consultar recomendación'),
              ),
            ],
          ),
        ),
        if (esperando) const LinearProgressIndicator(),
        SelectableText(resultado),
        const Divider(height: 32),
        Text(
          'Asistente del tutorial',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const Text(
          'Clasificador pequeño entrenado para entregas. No es el proyecto individual ni un LLM generativo.',
        ),
        ...conversacion.map(
          (s) => Card(
            child: Padding(padding: const EdgeInsets.all(12), child: Text(s)),
          ),
        ),
        TextField(
          controller: mensaje,
          decoration: const InputDecoration(
            labelText: 'Mensaje o consulta con folio',
          ),
        ),
        FilledButton(
          onPressed: esperando
              ? null
              : () {
                  final m = mensaje.text.trim();
                  if (m.isEmpty) return;
                  setState(() => conversacion.add('Tú: $m'));
                  mensaje.clear();
                  llamar('/entregas/asistente/', {'mensaje': m}, chat: true);
                },
          child: const Text('Enviar al asistente'),
        ),
      ],
    ),
  );
}
