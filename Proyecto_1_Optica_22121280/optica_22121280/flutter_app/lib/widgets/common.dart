import 'package:flutter/material.dart';

const ink = Color(0xFF302638);
const accent = Color(0xFFE1D5F3);
const cream = Color(0xFFFAF9F6);
const muted = Color(0xFF726B78);
const line = Color(0xFFE6E1E8);
const lilac = Color(0xFFF0EAF7);

class PageBody extends StatelessWidget {
  final Widget child;
  final double maxWidth;
  const PageBody({super.key, required this.child, this.maxWidth = 840});
  @override
  Widget build(BuildContext context) => Align(
    alignment: Alignment.topCenter,
    child: ConstrainedBox(
      constraints: BoxConstraints(maxWidth: maxWidth),
      child: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: MediaQuery.sizeOf(context).width < 600 ? 22 : 48,
          vertical: 32,
        ),
        child: child,
      ),
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

class EyewearPhoto extends StatelessWidget {
  final String code;
  final double height;
  const EyewearPhoto({super.key, required this.code, this.height = 140});

  static const descriptions = {
    'esencial': 'Foto de lentes redondos con armazón dorado',
    'antirreflejante': 'Foto de lentes con armazón negro',
    'fotocromatico': 'Foto de lentes con armazón negro y rosa',
    'premium': 'Foto de lentes con armazón carey',
  };

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(4),
    child: ColoredBox(
      color: Colors.white,
      child: Image.asset(
        'assets/images/${descriptions.containsKey(code) ? code : 'esencial'}.jpg',
        height: height,
        width: double.infinity,
        fit: BoxFit.contain,
        semanticLabel: descriptions[code] ?? 'Foto de lentes de referencia',
      ),
    ),
  );
}

class SectionIntro extends StatelessWidget {
  final String eyebrow, title, description;
  const SectionIntro({
    super.key,
    required this.eyebrow,
    required this.title,
    required this.description,
  });
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        eyebrow,
        style: const TextStyle(
          fontSize: 11,
          letterSpacing: 2.5,
          color: muted,
          fontWeight: FontWeight.w600,
        ),
      ),
      const SizedBox(height: 16),
      Text(
        title,
        style: TextStyle(
          fontSize: MediaQuery.sizeOf(context).width < 600 ? 34 : 46,
          height: 1.12,
          letterSpacing: -1.5,
          fontWeight: FontWeight.w400,
          color: ink,
        ),
      ),
      const SizedBox(height: 14),
      Text(description, style: const TextStyle(color: muted, height: 1.7)),
      const SizedBox(height: 30),
    ],
  );
}
