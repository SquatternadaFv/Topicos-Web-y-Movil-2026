import json
import uuid
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import OpticaService, paquete_json, orden_json
from .validation import ErrorDominio

servicio = OpticaService()

def api(metodos):
    def decorar(fn):
        @wraps(fn)
        def vista(request, *args, **kwargs):
            if request.method not in metodos:
                response = JsonResponse({'error': 'Método no permitido.'}, status=405)
                response['Allow'] = ', '.join(metodos)
                return response
            try:
                return fn(request, *args, **kwargs)
            except ErrorDominio as exc:
                return JsonResponse({'error': str(exc), 'campos': exc.campos}, status=exc.status, json_dumps_params={'ensure_ascii': False})
        # Endpoints públicos sin sesión; CSRF del admin sigue activo.
        return csrf_exempt(vista)
    return decorar

def cuerpo(request):
    if request.content_type != 'application/json':
        raise ErrorDominio('Usa Content-Type: application/json.', 415)
    if len(request.body) > 8192:
        raise ErrorDominio('El cuerpo excede el máximo de 8 KB.', 413)
    try:
        return json.loads(request.body.decode('utf-8'), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeDecodeError):
        raise ErrorDominio('JSON inválido.')

@api(['GET'])
def salud(request):
    return JsonResponse({'estado': 'ok', 'proyecto': 'Optica 22121280'})

@api(['GET'])
def catalogo(request):
    return JsonResponse({'resultados': [paquete_json(p) for p in servicio.catalogo.listar(request.GET.get('q', '').strip()[:100])]})

@api(['GET'])
def detalle(request, codigo):
    paquete = servicio.catalogo.obtener(codigo)
    if not paquete:
        raise ErrorDominio('Paquete no encontrado.', 404)
    return JsonResponse(paquete_json(paquete))

@api(['POST'])
def recomendar(request):
    return JsonResponse(servicio.recomendar(cuerpo(request)))

@api(['POST'])
def registrar(request):
    try:
        clave = uuid.UUID(request.headers.get('Idempotency-Key', ''))
    except ValueError:
        raise ErrorDominio('Envía Idempotency-Key con un UUID válido.')
    orden, creada = servicio.registrar(cuerpo(request), clave)
    return JsonResponse(orden_json(orden), status=201 if creada else 200)

@api(['GET'])
def consultar(request, folio):
    orden = servicio.ordenes.por_folio(folio)
    if not orden:
        raise ErrorDominio('No se encontró una orden con ese folio.', 404)
    return JsonResponse(orden_json(orden))

@api(['POST'])
def asistente(request):
    from .asistente import AsistenteService
    return JsonResponse(AsistenteService().responder(cuerpo(request)),json_dumps_params={'ensure_ascii':False})
