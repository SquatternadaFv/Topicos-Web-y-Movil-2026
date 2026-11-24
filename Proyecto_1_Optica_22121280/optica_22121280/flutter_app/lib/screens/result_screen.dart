import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../data/api_client.dart';
import '../models/models.dart';
import '../widgets/common.dart';
import 'order_screen.dart';

class RecommendationView extends StatelessWidget {
  final Recomendacion result;
  const RecommendationView({super.key, required this.result});
  String pct(double p) => '${(p * 100).toStringAsFixed(1)}%';
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      EyewearPhoto(code: result.paquete.codigo, height: 170),
      const SizedBox(height: 20),
      const Text(
        'TU PAQUETE SUGERIDO',
        style: TextStyle(letterSpacing: 2, color: ink, fontSize: 11),
      ),
      const SizedBox(height: 10),
      Text(
        result.paquete.nombre,
        style: const TextStyle(
          fontSize: 36,
          color: ink,
          fontWeight: FontWeight.w600,
        ),
      ),
      Text(
        '\$${result.paquete.precio} MXN',
        style: const TextStyle(fontSize: 22, color: ink),
      ),
      const SizedBox(height: 18),
      Wrap(
        spacing: 8,
        children: result.paquete.tratamientos
            .map((t) => Chip(label: Text(t)))
            .toList(),
      ),
      const SizedBox(height: 12),
      Card(
        elevation: 0,
        color: result.corregido ? const Color(0xFFFFEECF) : lilac,
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                result.corregido
                    ? 'Ajustado por reglas comerciales'
                    : 'Modelo y reglas coinciden',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 17,
                ),
              ),
              const SizedBox(height: 10),
              Text(result.json['motivo'] as String),
              const SizedBox(height: 10),
              Text(
                'Opción original: ${result.json['original']} · ${pct(result.confianzaOriginal)}',
              ),
              Text(
                'Confianza del modelo para la opción final: ${pct(result.confianza)}',
              ),
            ],
          ),
        ),
      ),
      const SizedBox(height: 22),
      const Text(
        'Todas las alternativas',
        style: TextStyle(fontSize: 21, fontWeight: FontWeight.w600),
      ),
      const SizedBox(height: 8),
      ...result.ranking.map(
        (r) => Card(
          elevation: 0,
          color: Colors.white,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      r['elegible'] as bool
                          ? Icons.check_circle_outline
                          : Icons.block,
                      size: 20,
                      color: r['elegible'] as bool ? ink : Colors.brown,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        r['nombre'] as String,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                    Text(pct((r['probabilidad'] as num).toDouble())),
                  ],
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(
                  value: (r['probabilidad'] as num).toDouble(),
                  minHeight: 5,
                  borderRadius: BorderRadius.circular(8),
                ),
                const SizedBox(height: 8),
                Text(
                  (r['motivos'] as List).isEmpty
                      ? 'Cumple las reglas · \$${r['precio']} MXN'
                      : (r['motivos'] as List).join(' '),
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
        ),
      ),
      const SizedBox(height: 14),
      const Text(
        'La confianza expresa la distribución del modelo entrenado; no es garantía de calidad ni probabilidad de éxito clínico. Las reglas pueden elegir una alternativa con baja confianza.',
        style: TextStyle(fontSize: 12, color: Colors.black54),
      ),
      const SizedBox(height: 10),
      Text(
        result.json['aviso'] as String,
        style: const TextStyle(fontSize: 12, color: Colors.black54),
      ),
    ],
  );
}

class ResultScreen extends StatefulWidget {
  final ApiClient api;
  final Recomendacion recommendation;
  const ResultScreen({
    super.key,
    required this.api,
    required this.recommendation,
  });
  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final key = const Uuid().v4();
  bool loading = false;
  String? error;
  Future<void> confirm() async {
    final accepted = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Registrar solicitud'),
        content: const Text(
          'Confirma tu solicitud con el precio y la disponibilidad vigentes. Recibirás un folio para consultarla después. No se realizará ningún cobro.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Volver'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Confirmar registro'),
          ),
        ],
      ),
    );
    if (accepted != true || !mounted) {
      return;
    }
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final order = await widget.api.registrar(
        widget.recommendation.entradas,
        key,
      );
      if (!mounted) {
        return;
      }
      Navigator.pushReplacement(
        context,
        MaterialPageRoute<void>(
          builder: (_) => OrderDetailScreen(order: order, justCreated: true),
        ),
      );
    } catch (e) {
      if (mounted) {
        setState(() => error = e.toString());
      }
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Tu recomendación')),
    body: SingleChildScrollView(
      child: PageBody(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            RecommendationView(result: widget.recommendation),
            const SizedBox(height: 24),
            if (error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(error!, style: const TextStyle(color: Colors.red)),
              ),
            FilledButton.icon(
              onPressed: loading ? null : confirm,
              icon: loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.check),
              label: Text(
                loading
                    ? 'Registrando…'
                    : 'Registrar solicitud y obtener folio',
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    ),
  );
}
