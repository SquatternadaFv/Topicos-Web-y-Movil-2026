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
          maxWidth: 1340,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _CollectionHero(onRecommend: widget.onRecommend),
              const SizedBox(height: 28),
              const _ServicesStrip(),
              const SizedBox(height: 36),
              const Text(
                'LA COLECCIÓN',
                style: TextStyle(
                  fontSize: 11,
                  color: muted,
                  letterSpacing: 2.5,
                ),
              ),
              const SizedBox(height: 28),
              const Text(
                'Una mirada para cada día.',
                style: TextStyle(
                  fontSize: 34,
                  letterSpacing: -1,
                  fontWeight: FontWeight.w600,
                  color: ink,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Cuatro paquetes. Encuentra el que acompaña tu rutina.',
              ),
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
                        crossAxisCount: constraints.maxWidth > 1000
                            ? 4
                            : constraints.maxWidth > 600
                            ? 2
                            : 1,
                        mainAxisExtent: 350,
                        mainAxisSpacing: 18,
                        crossAxisSpacing: 18,
                      ),
                      itemBuilder: (context, index) {
                        final p = items[index];
                        void openDetail() => Navigator.push(
                          context,
                          MaterialPageRoute<void>(
                            builder: (_) =>
                                DetailScreen(api: widget.api, codigo: p.codigo),
                          ),
                        );
                        return Semantics(
                          button: true,
                          excludeSemantics: true,
                          label:
                              '${p.nombre}. \$${p.precio} MXN. ${p.tratamientos.join(', ')}. ${p.disponible ? 'Disponible' : 'Sin disponibilidad'}. Ver detalle.',
                          onTap: openDetail,
                          child: Card(
                            elevation: 0,
                            color: Colors.white,
                            margin: EdgeInsets.zero,
                            child: InkWell(
                              borderRadius: BorderRadius.circular(8),
                              onTap: openDetail,
                              child: Padding(
                                padding: const EdgeInsets.all(16),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    EyewearPhoto(code: p.codigo, height: 168),
                                    const SizedBox(height: 14),
                                    Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            p.nombre,
                                            style: const TextStyle(
                                              fontSize: 19,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                        ),
                                        Text(
                                          '\$${p.precio}',
                                          style: const TextStyle(
                                            fontSize: 14,
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
                                        Expanded(
                                          child: Text(
                                            p.disponible
                                                ? 'Disponible'
                                                : 'Sin disponibilidad',
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: p.disponible
                                                  ? ink
                                                  : Colors.red,
                                            ),
                                          ),
                                        ),
                                        const Text(
                                          'Ver detalle',
                                          style: TextStyle(fontSize: 12),
                                        ),
                                        const SizedBox(width: 8),
                                        const Icon(
                                          Icons.arrow_forward,
                                          size: 18,
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
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
                'Fotografías de armazones como referencia visual. Precios de demostración en MXN. La graduación requiere valoración profesional.',
                style: TextStyle(fontSize: 12, color: Colors.black54),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class _CollectionHero extends StatelessWidget {
  final VoidCallback onRecommend;
  const _CollectionHero({required this.onRecommend});

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final wide = constraints.maxWidth >= 720;
      final copy = Padding(
        padding: EdgeInsets.all(wide ? 48 : 26),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'OTRA FORMA DE MIRAR',
              style: TextStyle(
                fontSize: 10,
                letterSpacing: 2.5,
                fontWeight: FontWeight.w600,
                color: muted,
              ),
            ),
            const SizedBox(height: 28),
            Text(
              'Tu rutina.\nTu forma\nde ver.',
              style: TextStyle(
                fontSize: wide ? 68 : 49,
                height: 1.02,
                letterSpacing: -3,
                color: ink,
                fontWeight: FontWeight.w400,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Diseño que va contigo.\nTratamientos que se adaptan a tu día.',
              style: TextStyle(color: muted, height: 1.7, fontSize: 15),
            ),
            const SizedBox(height: 28),
            FilledButton.icon(
              onPressed: onRecommend,
              iconAlignment: IconAlignment.end,
              icon: const Icon(Icons.arrow_outward, size: 18),
              label: const Text('Encontrar mi paquete'),
            ),
          ],
        ),
      );
      final art = Container(
        height: wide ? 500 : 260,
        color: Colors.white,
        child: Stack(
          alignment: Alignment.center,
          children: [
            Positioned.fill(
              child: Image.asset(
                'assets/images/portada.jpg',
                fit: BoxFit.contain,
                semanticLabel: 'Fotografía de una selección de lentes reales',
              ),
            ),
            const Positioned(
              left: 24,
              top: 26,
              child: Text(
                'L / 01',
                style: TextStyle(fontSize: 11, letterSpacing: 2, color: ink),
              ),
            ),
            const Positioned(
              right: 24,
              bottom: 26,
              child: Text(
                'PERSPECTIVA PROPIA.',
                style: TextStyle(fontSize: 10, letterSpacing: 2, color: ink),
              ),
            ),
          ],
        ),
      );
      return ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: ColoredBox(
          color: const Color(0xFFF0EEEA),
          child: wide
              ? Row(
                  children: [
                    Expanded(child: copy),
                    Expanded(child: art),
                  ],
                )
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [copy, art],
                ),
        ),
      );
    },
  );
}

class _ServicesStrip extends StatelessWidget {
  const _ServicesStrip();
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (_, constraints) {
      const items = [
        (Icons.tune_rounded, 'A tu medida', 'Según tu rutina y presupuesto'),
        (
          Icons.layers_outlined,
          'Elige con claridad',
          'Compara cada tratamiento',
        ),
        (
          Icons.receipt_long_outlined,
          'Siempre a la mano',
          'Consulta tu solicitud por folio',
        ),
      ];
      final narrow = constraints.maxWidth < 600;
      final children = items
          .map(
            (item) => Padding(
              padding: EdgeInsets.symmetric(vertical: narrow ? 12 : 20),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(item.$1, size: 22, color: muted),
                  const SizedBox(width: 14),
                  Flexible(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.$2,
                          style: const TextStyle(
                            fontWeight: FontWeight.w500,
                            fontSize: 13,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          item.$3,
                          style: const TextStyle(color: muted, fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          )
          .toList();
      return Container(
        decoration: const BoxDecoration(
          border: Border(bottom: BorderSide(color: line)),
        ),
        child: narrow
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: children,
              )
            : Row(
                children: children
                    .map((child) => Expanded(child: child))
                    .toList(),
              ),
      );
    },
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
                EyewearPhoto(code: p.codigo, height: 320),
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
                  'Fotografía de referencia del armazón. Los tratamientos corresponden a la descripción del paquete de demostración; no incluye una prescripción ni una graduación automática.',
                ),
              ],
            ),
          ),
        );
      },
    ),
  );
}
