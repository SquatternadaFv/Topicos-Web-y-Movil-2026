import 'package:flutter/material.dart';
import '../data/api_client.dart';
import '../models/models.dart';
import '../widgets/common.dart';

class ChatScreen extends StatefulWidget {
  final ApiClient api;
  final VoidCallback onRecommend;
  const ChatScreen({super.key, required this.api, required this.onRecommend});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final message = TextEditingController();
  final folio = TextEditingController();
  final scroll = ScrollController();
  final List<Json> messages = [];
  bool busy = false;
  String? error;

  @override
  void dispose() {
    message.dispose();
    folio.dispose();
    scroll.dispose();
    super.dispose();
  }

  Future<void> send([String? example]) async {
    final text = (example ?? message.text).trim();
    if (busy || text.isEmpty) return;
    if (text.length > 1000) {
      setState(() => error = 'Escribe hasta 1000 caracteres por mensaje.');
      return;
    }
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final response = await widget.api.conversar(text, folio: folio.text);
      if (!mounted) return;
      setState(() {
        messages.add({'usuario': text});
        messages.add(response);
        message.clear();
      });
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (scroll.hasClients) {
          scroll.animateTo(
            scroll.position.maxScrollExtent,
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOut,
          );
        }
      });
    } on ApiException catch (e) {
      if (mounted) setState(() => error = e.message);
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Widget bubble(Json item) {
    final user = item.containsKey('usuario');
    final sources = item['fuentes'] as List? ?? [];
    return Align(
      alignment: user ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 760),
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: user
              ? Theme.of(context).colorScheme.primaryContainer
              : Colors.white,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              user ? 'Tú' : 'Asistente Lúmina',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            SelectionArea(
              child: Text((item['usuario'] ?? item['respuesta']) as String),
            ),
            for (final source in sources)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  'Fuente: ${source['titulo']} · v${source['version']}',
                ),
              ),
            if (item['accion'] == 'abrir_recomendador')
              TextButton.icon(
                onPressed: widget.onRecommend,
                icon: const Icon(Icons.auto_awesome),
                label: const Text('Completar mi perfil'),
              ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Center(
    child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 840),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(22, 24, 22, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Tu asistente de óptica',
              style: const TextStyle(
                fontSize: 28,
                color: ink,
                letterSpacing: -1,
              ),
            ),
            const SizedBox(height: 4),
            const Text('Un poco de orientación para elegir mejor.'),
            const SizedBox(height: 8),
            TextField(
              controller: folio,
              enabled: !busy,
              decoration: const InputDecoration(
                labelText: 'Folio de referencia (opcional)',
                hintText: 'Pega el UUID de tu solicitud',
                isDense: true,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [
                for (final text in [
                  'Hola',
                  'Qué paquetes ofrecen',
                  'Quiero rastrear mi orden',
                ])
                  ActionChip(
                    label: Text(text),
                    onPressed: busy ? null : () => send(text),
                  ),
              ],
            ),
            Expanded(
              child: messages.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.blur_on_rounded, size: 48, color: muted),
                          SizedBox(height: 14),
                          Text(
                            'Hablemos de tu próxima mirada.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 21,
                              letterSpacing: -.5,
                              color: ink,
                            ),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Escribe un mensaje para comenzar.',
                            style: TextStyle(color: muted, fontSize: 12),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      controller: scroll,
                      itemCount: messages.length,
                      itemBuilder: (_, i) => bubble(messages[i]),
                    ),
            ),
            if (busy)
              const LinearProgressIndicator(
                semanticsLabel: 'Consultando asistente',
              ),
            if (error != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Text(
                  error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: TextField(
                    controller: message,
                    enabled: !busy,
                    minLines: 1,
                    maxLines: 3,
                    maxLength: 1000,
                    decoration: const InputDecoration(
                      labelText: 'Mensaje',
                      counterText: '',
                    ),
                    onSubmitted: (_) => send(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  tooltip: 'Enviar mensaje',
                  onPressed: busy ? null : () => send(),
                  icon: const Icon(Icons.send),
                ),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}
