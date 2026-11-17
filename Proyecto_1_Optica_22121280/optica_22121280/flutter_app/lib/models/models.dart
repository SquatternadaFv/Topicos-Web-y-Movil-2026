typedef Json = Map<String, dynamic>;

class Paquete {
  final String codigo, nombre, descripcion, precio;
  final List<String> tratamientos;
  final bool disponible;
  Paquete.fromJson(Json j)
    : codigo = j['codigo'] as String,
      nombre = j['nombre'] as String,
      descripcion = j['descripcion'] as String,
      precio = j['precio'] as String,
      tratamientos = List<String>.from(j['tratamientos'] as List),
      disponible = j['disponible'] as bool;
}

class Recomendacion {
  final Json json;
  Recomendacion(this.json);
  Paquete get paquete => Paquete.fromJson(json['paquete'] as Json);
  bool get corregido => json['corregido'] as bool;
  double get confianza => (json['confianza'] as num).toDouble();
  double get confianzaOriginal =>
      (json['confianza_original'] as num).toDouble();
  List<Json> get ranking => (json['ranking'] as List).cast<Json>();
  Json get entradas => json['entradas'] as Json;
}

class Orden {
  final Json json;
  Orden(this.json);
  String get folio => json['folio'] as String;
  Recomendacion get recomendacion =>
      Recomendacion(json['recomendacion'] as Json);
}
