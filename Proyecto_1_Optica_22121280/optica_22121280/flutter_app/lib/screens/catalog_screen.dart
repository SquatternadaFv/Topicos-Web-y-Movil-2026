import 'package:flutter/material.dart';
import '../data/api_client.dart';
import '../models/models.dart';
import '../widgets/common.dart';

class CatalogScreen extends StatefulWidget {
  final ApiClient api;
  final VoidCallback onRecommend;
  const CatalogScreen({
    super.key,
    required this.api,
    required this.onRecommend,
  });
  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  final search = TextEditingController();
  late Future<List<Paquete>> future;
  @override
  void initState() {
    super.initState();
    future = widget.api.catalogo('');
  }

  @override
  void dispose() {
    search.dispose();
    super.dispose();
  }

  Future<void> reload() async {
    setState(() {
      future = widget.api.catalogo(search.text);
    });
    try {
      await future;
    } catch (_) {
      /* FutureBuilder presenta el error. */
    }
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: reload,
    child: ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        PageBody(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(28),
                decoration: BoxDecoration(
                  color: ink,
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'ENCUENTRA TU PAQUETE',
                      style: TextStyle(
                        color: accent,
                        letterSpacing: 2,
                        fontSize: 11,
                      ),
                    ),
                    const SizedBox(height: 14),
                    const Text(
                      'Tu rutina.\nTu forma de ver.',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 38,
                        height: 1.1,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Compara tratamientos y descubre una opción\nsegún tus preferencias y presupuesto.',
                      style: TextStyle(color: Color(0xFFCDDDD4), height: 1.6),
                    ),
                    const SizedBox(height: 22),
                    FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: accent,
                        foregroundColor: ink,
                      ),
                      onPressed: widget.onRecommend,
                      icon: const Icon(Icons.arrow_outward),
                      label: const Text('Encontrar mi paquete'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),
              const Text(
                'Colección de paquetes',
                style: TextStyle(
                  fontSize: 25,
                  fontWeight: FontWeight.w600,
                  color: ink,
                ),
              ),
              const SizedBox(height: 8),
              const Text('Precios de demostración en MXN · 4 opciones'),
              const SizedBox(height: 18),
              TextField(
                controller: search,
                onSubmitted: (_) => reload(),
                decoration: InputDecoration(
                  labelText: 'Buscar por nombre',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: IconButton(
                    onPressed: reload,
                    icon: const Icon(Icons.arrow_forward),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              FutureBuilder<List<Paquete>>(
                future: future,
                builder: (context, snapshot) {
                  if (snapshot.connectionState != ConnectionState.done) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return ErrorPanel(error: snapshot.error!, retry: reload);
                  }
                  final items = snapshot.data!;
                  if (items.isEmpty) {
                    return const Padding(
                      padding: EdgeInsets.all(32),
                      child: Text(
                        'No hay paquetes con ese nombre. Prueba otra búsqueda.',
                      ),
                    );
                  }
                  return LayoutBuilder(
                    builder: (context, constraints) => GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: items.length,
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: constraints.maxWidth > 650 ? 2 : 1,
                        mainAxisExtent: 310,
                        mainAxisSpacing: 18,
                        crossAxisSpacing: 18,
                      ),
                      itemBuilder: (context, index) {
                        final p = items[index];
                        return Card(
                          elevation: 0,
                          color: Colors.white,
                          margin: EdgeInsets.zero,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(12),
                            onTap: () => Navigator.push(
                              context,
                              MaterialPageRoute<void>(
                                builder: (_) => DetailScreen(
                                  api: widget.api,
                                  codigo: p.codigo,
                                ),
                              ),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  EyewearArt(code: p.codigo),
                                  const SizedBox(height: 14),
                                  Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          p.nombre,
                                          style: const TextStyle(
                                            fontSize: 21,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                      Text(
                                        '\$${p.precio}',
                                        style: const TextStyle(
                                          fontSize: 17,
                                          color: ink,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    p.tratamientos.join(' · '),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const Spacer(),
                                  Row(
                                    children: [
                                      Text(
                                        p.disponible
                                            ? 'Disponible'
                                            : 'Sin disponibilidad',
                                        style: TextStyle(
                                          color: p.disponible
                                              ? ink
                                              : Colors.red,
                                        ),
                                      ),
                                      const Spacer(),
                                      const Text('Ver detalle'),
                                      const SizedBox(width: 8),
                                      const Icon(Icons.arrow_forward, size: 18),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
              const SizedBox(height: 20),
              const Text(
                'Orientación comercial académica. La graduación requiere valoración profesional.',
                style: TextStyle(fontSize: 12, color: Colors.black54),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class DetailScreen extends StatefulWidget {
  final ApiClient api;
  final String codigo;
  const DetailScreen({super.key, required this.api, required this.codigo});
  @override
  State<DetailScreen> createState() => _DetailScreenState();
}

class _DetailScreenState extends State<DetailScreen> {
  late Future<Paquete> future;
  @override
  void initState() {
    super.initState();
    future = widget.api.detalle(widget.codigo);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Detalle del paquete')),
    body: FutureBuilder<Paquete>(
      future: future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return ErrorPanel(
            error: snapshot.error!,
            retry: () => setState(() {
              future = widget.api.detalle(widget.codigo);
            }),
          );
        }
        final p = snapshot.data!;
        return SingleChildScrollView(
          child: PageBody(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                EyewearArt(code: p.codigo, height: 240),
                const SizedBox(height: 28),
                Text(
                  p.nombre,
                  style: const TextStyle(fontSize: 36, color: ink),
                ),
                Text('\$${p.precio} MXN', style: const TextStyle(fontSize: 24)),
                const SizedBox(height: 20),
                Text(p.descripcion),
                const SizedBox(height: 18),
                ...p.tratamientos.map(
                  (t) => ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.check_circle_outline),
                    title: Text(t),
                  ),
                ),
                Text(
                  p.disponible
                      ? 'Disponible para recomendar'
                      : 'Temporalmente no disponible',
                ),
                const SizedBox(height: 20),
                const Text(
                  'La ilustración es conceptual. Paquete de demostración; no incluye una prescripción ni una graduación automática.',
                ),
              ],
            ),
          ),
        );
      },
    ),
  );
}
