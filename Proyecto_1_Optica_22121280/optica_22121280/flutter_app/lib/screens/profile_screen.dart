import 'package:flutter/material.dart';
import '../data/api_client.dart';
import '../models/models.dart';
import '../widgets/common.dart';
import 'result_screen.dart';

class ProfileScreen extends StatefulWidget {
  final ApiClient api;
  const ProfileScreen({super.key, required this.api});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final form = GlobalKey<FormState>();
  final pantalla = TextEditingController(text: '8');
  final exterior = TextEditingController(text: '1');
  final presupuesto = TextEditingController(text: '700');
  String uso = 'oficina';
  bool foto = false, loading = false;
  String? error;
  @override
  void dispose() {
    pantalla.dispose();
    exterior.dispose();
    presupuesto.dispose();
    super.dispose();
  }

  String? number(String? s, double max, {double min = 0, bool money = false}) {
    final n = double.tryParse((s ?? '').replaceAll(',', '.'));
    if (n == null || !n.isFinite || n < min || n > max) {
      return 'Ingresa un valor entre $min y $max.';
    }
    if (money && !RegExp(r'^\d+(?:[.,]\d{1,2})?$').hasMatch(s ?? '')) {
      return 'Usa como máximo dos decimales.';
    }
    return null;
  }

  Future<void> submit() async {
    if (!form.currentState!.validate()) {
      return;
    }
    setState(() {
      loading = true;
      error = null;
    });
    final Json profile = {
      'horas_pantalla': double.parse(pantalla.text.replaceAll(',', '.')),
      'horas_exterior': double.parse(exterior.text.replaceAll(',', '.')),
      'presupuesto': double.parse(presupuesto.text.replaceAll(',', '.')),
      'uso_principal': uso,
      'prefiere_fotocromatico': foto,
    };
    try {
      final result = await widget.api.recomendar(profile);
      if (!mounted) {
        return;
      }
      await Navigator.push(
        context,
        MaterialPageRoute<void>(
          builder: (_) => ResultScreen(api: widget.api, recommendation: result),
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
              '01 / TU PERFIL',
              style: TextStyle(color: ink, letterSpacing: 2, fontSize: 12),
            ),
            const SizedBox(height: 14),
            const Text(
              'Un paquete a tu medida.',
              style: TextStyle(
                fontSize: 32,
                color: ink,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Cuéntanos sobre tu rutina. La recomendación combina un modelo entrenado con reglas de presupuesto y disponibilidad.',
            ),
            const SizedBox(height: 28),
            TextFormField(
              key: const Key('pantalla'),
              controller: pantalla,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: const InputDecoration(
                labelText: 'Horas de pantalla al día',
                helperText: 'Entre 0 y 16 horas',
                prefixIcon: Icon(Icons.computer),
              ),
              validator: (s) => number(s, 16),
            ),
            const SizedBox(height: 20),
            TextFormField(
              key: const Key('exterior'),
              controller: exterior,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: const InputDecoration(
                labelText: 'Horas en exteriores al día',
                helperText: 'Entre 0 y 12 horas',
                prefixIcon: Icon(Icons.wb_sunny_outlined),
              ),
              validator: (s) => number(s, 12),
            ),
            const SizedBox(height: 20),
            TextFormField(
              key: const Key('presupuesto'),
              controller: presupuesto,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: const InputDecoration(
                labelText: 'Presupuesto máximo (MXN)',
                helperText: 'Entre \$300 y \$10,000. Paquetes desde \$650.',
                prefixIcon: Icon(Icons.payments_outlined),
              ),
              validator: (s) => number(s, 10000, min: 300, money: true),
            ),
            const SizedBox(height: 20),
            DropdownButtonFormField<String>(
              initialValue: uso,
              decoration: const InputDecoration(labelText: 'Uso principal'),
              items: const [
                DropdownMenuItem(
                  value: 'general',
                  child: Text('Uso cotidiano'),
                ),
                DropdownMenuItem(value: 'estudio', child: Text('Estudio')),
                DropdownMenuItem(value: 'oficina', child: Text('Oficina')),
                DropdownMenuItem(value: 'exterior', child: Text('Exteriores')),
              ],
              onChanged: loading ? null : (s) => setState(() => uso = s!),
            ),
            const SizedBox(height: 12),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Quiero tratamiento fotocromático'),
              subtitle: const Text(
                'Preferencia obligatoria al activarla. Paquetes desde \$1,800.',
              ),
              value: foto,
              onChanged: loading ? null : (v) => setState(() => foto = v),
            ),
            const SizedBox(height: 20),
            if (error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(
                  error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            FilledButton.icon(
              key: const Key('recommend'),
              onPressed: loading ? null : submit,
              icon: loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.auto_awesome),
              label: Text(
                loading ? 'Consultando modelo…' : 'Obtener recomendación',
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Datos sintéticos para una demostración académica. No se calculan diagnósticos ni graduaciones.',
              style: TextStyle(fontSize: 12, color: Colors.black54),
            ),
          ],
        ),
      ),
    ),
  );
}
