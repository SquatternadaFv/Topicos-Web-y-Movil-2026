import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../data/api_client.dart';
import '../models/models.dart';
import '../widgets/common.dart';
import 'result_screen.dart';

class OrderLookupScreen extends StatefulWidget {
  final ApiClient api;
  const OrderLookupScreen({super.key, required this.api});
  @override
  State<OrderLookupScreen> createState() => _OrderLookupScreenState();
}

class _OrderLookupScreenState extends State<OrderLookupScreen> {
  final controller = TextEditingController();
  final form = GlobalKey<FormState>();
  bool loading = false;
  String? error;
  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> search() async {
    if (!form.currentState!.validate()) {
      return;
    }
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final order = await widget.api.consultar(controller.text);
      if (!mounted) {
        return;
      }
      await Navigator.push(
        context,
        MaterialPageRoute<void>(
          builder: (_) => OrderDetailScreen(order: order),
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
  Widget build(BuildContext context) => SingleChildScrollView(
    child: PageBody(
      child: Form(
        key: form,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'TU SOLICITUD, A LA MANO',
              style: TextStyle(letterSpacing: 2, color: ink, fontSize: 12),
            ),
            const SizedBox(height: 16),
            const Text(
              'Consulta tu folio.',
              style: TextStyle(fontSize: 34, color: ink),
            ),
            const SizedBox(height: 12),
            const Text(
              'Pega el identificador que recibiste al registrar tu solicitud.',
            ),
            const SizedBox(height: 28),
            TextFormField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'Folio de la solicitud',
                prefixIcon: Icon(Icons.receipt_long_outlined),
              ),
              validator: (v) =>
                  RegExp(
                    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
                  ).hasMatch((v ?? '').trim())
                  ? null
                  : 'Pega el folio completo con sus guiones.',
            ),
            const SizedBox(height: 20),
            if (error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(error!, style: const TextStyle(color: Colors.red)),
              ),
            FilledButton.icon(
              onPressed: loading ? null : search,
              icon: loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.search),
              label: const Text('Consultar solicitud'),
            ),
          ],
        ),
      ),
    ),
  );
}

class OrderDetailScreen extends StatelessWidget {
  final Orden order;
  final bool justCreated;
  const OrderDetailScreen({
    super.key,
    required this.order,
    this.justCreated = false,
  });
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(
        justCreated ? 'Solicitud registrada' : 'Detalle de la solicitud',
      ),
    ),
    body: SingleChildScrollView(
      child: PageBody(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: ink,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(
                    Icons.check_circle_outline,
                    color: accent,
                    size: 38,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    justCreated
                        ? 'Listo. Tu solicitud quedó guardada.'
                        : 'Encontramos tu solicitud.',
                    style: const TextStyle(color: Colors.white, fontSize: 24),
                  ),
                  const SizedBox(height: 18),
                  const Text(
                    'FOLIO',
                    style: TextStyle(color: accent, letterSpacing: 2),
                  ),
                  const SizedBox(height: 8),
                  SelectableText(
                    order.folio,
                    style: const TextStyle(color: Colors.white, fontSize: 17),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                    ),
                    onPressed: () async {
                      await Clipboard.setData(ClipboardData(text: order.folio));
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Folio copiado')),
                        );
                      }
                    },
                    icon: const Icon(Icons.copy, size: 16),
                    label: const Text('Copiar folio'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Text(
              'Estado: ${order.json['estado']} · Total registrado: \$${order.json['precio_confirmado']} MXN',
            ),
            const SizedBox(height: 8),
            Text(
              'Fecha: ${DateTime.parse(order.json['creada'] as String).toLocal()}',
            ),
            const SizedBox(height: 16),
            const Text(
              'Perfil registrado',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              'Pantalla: ${order.json['entradas']['horas_pantalla']} h · Exterior: ${order.json['entradas']['horas_exterior']} h\nPresupuesto: \$${order.json['entradas']['presupuesto']} · Uso: ${order.json['entradas']['uso_principal']}\nFotocromático obligatorio: ${order.json['entradas']['prefiere_fotocromatico'] == true ? 'Sí' : 'No'}',
            ),
            const SizedBox(height: 24),
            RecommendationView(result: order.recomendacion),
            const SizedBox(height: 24),
          ],
        ),
      ),
    ),
  );
}
