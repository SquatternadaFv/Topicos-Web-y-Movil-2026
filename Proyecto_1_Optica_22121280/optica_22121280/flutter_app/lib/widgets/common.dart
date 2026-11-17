import 'package:flutter/material.dart';

const ink = Color(0xFF163B38);
const accent = Color(0xFFCEEB87);
const cream = Color(0xFFF7F8F2);

class PageBody extends StatelessWidget {
  final Widget child;
  const PageBody({super.key, required this.child});
  @override
  Widget build(BuildContext context) => Align(
    alignment: Alignment.topCenter,
    child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 1000),
      child: Padding(padding: const EdgeInsets.all(24), child: child),
    ),
  );
}

class ErrorPanel extends StatelessWidget {
  final Object error;
  final VoidCallback retry;
  const ErrorPanel({super.key, required this.error, required this.retry});
  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.cloud_off_outlined, size: 40),
          const SizedBox(height: 16),
          Text(error.toString(), textAlign: TextAlign.center),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: retry,
            icon: const Icon(Icons.refresh),
            label: const Text('Reintentar'),
          ),
        ],
      ),
    ),
  );
}

class EyewearArt extends StatelessWidget {
  final String code;
  final double height;
  const EyewearArt({super.key, required this.code, this.height = 140});
  @override
  Widget build(BuildContext context) => Container(
    height: height,
    decoration: BoxDecoration(
      color: code == 'premium'
          ? const Color(0xFFE4E5DE)
          : code == 'fotocromatico'
          ? const Color(0xFFEAE6DC)
          : const Color(0xFFE4EEE8),
      borderRadius: BorderRadius.circular(20),
    ),
    child: Center(
      child: CustomPaint(
        size: const Size(220, 85),
        painter: GlassesPainter(code),
      ),
    ),
  );
}

class GlassesPainter extends CustomPainter {
  final String code;
  GlassesPainter(this.code);
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = ink
      ..strokeWidth = code == 'premium' ? 5 : 3
      ..style = PaintingStyle.stroke;
    final tint = Paint()
      ..color = (code == 'fotocromatico' || code == 'premium')
          ? const Color(0x44715F46)
          : const Color(0x2268B4A3);
    for (final x in [13.0, 122.0]) {
      final r = RRect.fromRectAndRadius(
        Rect.fromLTWH(x, 18, 85, 56),
        Radius.circular(code == 'esencial' ? 28 : 14),
      );
      canvas.drawRRect(r, tint);
      canvas.drawRRect(r, paint);
    }
    canvas.drawArc(
      const Rect.fromLTWH(98, 27, 24, 18),
      3.14,
      3.14,
      false,
      paint,
    );
    canvas.drawLine(const Offset(0, 22), const Offset(13, 34), paint);
    canvas.drawLine(const Offset(207, 34), const Offset(220, 22), paint);
  }

  @override
  bool shouldRepaint(covariant GlassesPainter oldDelegate) =>
      code != oldDelegate.code;
}
