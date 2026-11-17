"""Casos de uso. La API y Flutter no coordinan ORM, IA ni reglas."""
from django.db import transaction, IntegrityError
from .repositories import CatalogoRepository, OrdenRepository
from .recomendador import obtener_recomendador
from .reglas import motivos_descarte
from .validation import ErrorDominio, validar_entradas

AVISO = 'Orientación comercial académica con datos sintéticos. No determina graduación ni sustituye una valoración profesional.'

def paquete_json(p):
    return {'codigo': p.codigo, 'nombre': p.nombre, 'descripcion': p.descripcion, 'precio': str(p.precio), 'tratamientos': p.tratamientos, 'fotocromatico': p.fotocromatico, 'disponible': p.disponible}

class OpticaService:
    def __init__(self, predictor=None, catalogo=None, ordenes=None):
        self.predictor = predictor
        self.catalogo = catalogo or CatalogoRepository()
        self.ordenes = ordenes or OrdenRepository()

    def recomendar(self, datos):
        entradas = validar_entradas(datos)
        predictor = self.predictor or obtener_recomendador()
        ranking_modelo = predictor.ranking(entradas)
        catalogo = {p.codigo: p for p in self.catalogo.listar()}
        ranking = []
        for codigo, probabilidad in ranking_modelo:
            paquete = catalogo.get(codigo)
            motivos = motivos_descarte(paquete, entradas) if paquete else ['Paquete no activo en el catálogo.']
            ranking.append({'codigo': codigo, 'nombre': paquete.nombre if paquete else codigo, 'precio': str(paquete.precio) if paquete else None, 'probabilidad': round(probabilidad, 6), 'elegible': not motivos, 'motivos': motivos})
        elegida = next((r for r in ranking if r['elegible']), None)
        if elegida is None:
            raise ErrorDominio('No hay un paquete disponible que cumpla tu presupuesto y preferencias. Ajusta el perfil; no se registró una orden.', 422, {'ranking': ranking})
        original = ranking[0]
        corregido = original['codigo'] != elegida['codigo']
        return {'entradas': entradas, 'paquete': paquete_json(catalogo[elegida['codigo']]), 'original': original['codigo'], 'confianza_original': original['probabilidad'], 'confianza': elegida['probabilidad'], 'corregido': corregido, 'motivo': 'Se descartó la primera opción: ' + ' '.join(original['motivos']) if corregido else 'La primera opción del modelo cumple todas las reglas comerciales.', 'ranking': ranking, 'version_modelo': predictor.version, 'aviso': AVISO}

    def registrar(self, datos, clave):
        entradas = validar_entradas(datos)
        previa = self.ordenes.por_clave(clave)
        if previa:
            if previa.entradas != entradas:
                raise ErrorDominio('La clave de confirmación ya fue utilizada con otro perfil.', 409)
            return previa, False
        # Recalcular aquí impide aceptar precios o recomendaciones manipulados por el cliente.
        try:
            with transaction.atomic():
                resultado = self.recomendar(entradas)
                paquete = self.catalogo.obtener(resultado['paquete']['codigo'])
                orden = self.ordenes.crear(clave_idempotencia=clave, paquete=paquete, entradas=entradas, resultado=resultado, precio_confirmado=paquete.precio)
                return orden, True
        except IntegrityError:
            previa = self.ordenes.por_clave(clave)
            if previa and previa.entradas == entradas:
                return previa, False
            raise ErrorDominio('Conflicto al registrar la orden. Reintenta con una clave nueva.', 409)

def orden_json(o):
    return {'folio': str(o.folio), 'estado': o.estado, 'creada': o.creada.isoformat(), 'precio_confirmado': str(o.precio_confirmado), 'entradas': o.entradas, 'recomendacion': o.resultado}
