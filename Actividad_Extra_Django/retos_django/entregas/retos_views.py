"""Vistas de los retos; las variables globales solo son el contraejemplo."""
import os
import socket
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from entregas.reglas import elegir_medio
from entregas.validacion import leer_numero

visitas_en_memoria = 0
ultimo_folio_en_memoria = None
destino_en_memoria = None
pedidos_en_memoria = {}


def _copia():
    return {'atendido_por': socket.gethostname(), 'proceso': os.getpid()}


@require_GET
def hola(request):
    return HttpResponse('Hola. Plataforma de entregas.')


@require_GET
def estado(request):
    return JsonResponse({
        'servicio': 'entregas', 'version': 1,
        'medios_disponibles': ['camioneta', 'moto', 'bicicleta', 'dron'], **_copia(),
    })


@require_GET
def cotizar(request):
    try:
        km = leer_numero(request.GET, 'km')
        kg = leer_numero(request.GET, 'kg')
    except ValueError as error:
        return JsonResponse({'error': str(error)}, status=400)
    medio, motivo = elegir_medio(km, kg)
    return JsonResponse({'km': km, 'kg': kg, 'medio': medio, 'motivo': motivo})


@require_GET
def cliente_web(request):
    return render(request, 'entregas/cotizador.html')


@require_GET
def visitas(request):
    request.session['visitas'] = request.session.get('visitas', 0) + 1
    return JsonResponse({**_copia(), 'visitas': request.session['visitas']})


@require_GET
def visitas_mal(request):
    global visitas_en_memoria
    visitas_en_memoria += 1
    return JsonResponse({**_copia(), 'visitas': visitas_en_memoria})


def _leer_folio(request):
    folio = request.GET.get('folio', '').strip()
    if not folio or len(folio) > 64:
        raise ValueError('folio es obligatorio y debe tener hasta 64 caracteres.')
    return folio


@require_GET
def ultimo_mal(request):
    global ultimo_folio_en_memoria
    try:
        ultimo_folio_en_memoria = _leer_folio(request)
    except ValueError as error:
        return JsonResponse({'error': str(error)}, status=400)
    return JsonResponse({**_copia(), 'folio': ultimo_folio_en_memoria, 'almacenamiento': 'global'})


@require_GET
def ver_ultimo_mal(request):
    return JsonResponse({**_copia(), 'folio': ultimo_folio_en_memoria, 'almacenamiento': 'global'})


@require_GET
def ultimo(request):
    if settings.DEMO_ULTIMO_GLOBAL:
        return ultimo_mal(request)
    try:
        folio = _leer_folio(request)
    except ValueError as error:
        return JsonResponse({'error': str(error)}, status=400)
    request.session['ultimo_folio'] = folio
    return JsonResponse({**_copia(), 'folio': folio, 'almacenamiento': 'sesion-db'})


@require_GET
def ver_ultimo(request):
    if settings.DEMO_ULTIMO_GLOBAL:
        return ver_ultimo_mal(request)
    return JsonResponse({**_copia(), 'folio': request.session.get('ultimo_folio'), 'almacenamiento': 'sesion-db'})


@require_GET
def borrador_destino(request):
    global destino_en_memoria
    destino = request.GET.get('destino', '').strip()
    if not destino or len(destino) > 200:
        return JsonResponse({'error':'destino es obligatorio, máximo 200 caracteres'}, status=400)
    if settings.DEMO_BORRADOR_GLOBAL:
        destino_en_memoria = destino
    else:
        request.session['borrador_destino'] = destino
    return JsonResponse({**_copia(), 'destino': destino, 'almacenamiento':'global' if settings.DEMO_BORRADOR_GLOBAL else 'sesion-db'})


@require_GET
def borrador_confirmar(request):
    global destino_en_memoria
    if settings.DEMO_BORRADOR_GLOBAL:
        destino, destino_en_memoria = destino_en_memoria, None
    else:
        destino = request.session.pop('borrador_destino', None)
    if not destino:
        return JsonResponse({**_copia(), 'error':'No hay destino en el borrador'}, status=400)
    from entregas.services import registrar_pedido
    pedido = registrar_pedido('Bodega demo', destino, 1, 5)
    return JsonResponse({**_copia(), 'folio':str(pedido.folio), 'destino':pedido.destino}, status=201)


@require_GET
def pedidos_demo(request, malo=False):
    """Paso 18: alta/consulta didáctica por query, con versiones DB y memoria."""
    from entregas.models import Pedido
    from entregas.services import registrar_pedido
    folio=request.GET.get('folio')
    if folio:
        if malo:
            pedido=pedidos_en_memoria.get(folio)
            return JsonResponse({**_copia(), **(pedido or {'error':'pedido no encontrado'})},status=200 if pedido else 404)
        try:
            p=Pedido.objects.get(folio=folio)
        except (Pedido.DoesNotExist, ValueError):
            return JsonResponse({**_copia(),'error':'pedido no encontrado'},status=404)
        return JsonResponse({**_copia(),'folio':str(p.folio),'destino':p.destino})
    destino=request.GET.get('destino','Destino demo')
    p=registrar_pedido('Bodega demo',destino,1,5)
    dato={'folio':str(p.folio),'destino':p.destino}
    if malo:
        pedidos_en_memoria[str(p.folio)]=dato
        p.delete()
    return JsonResponse({**_copia(), **dato},status=201)
