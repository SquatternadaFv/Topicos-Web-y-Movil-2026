import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from entregas.models import Pedido


@csrf_exempt
@require_POST
def asistente(request):
    from laboratorio.asistente import clasificar,extraer_folio
    try:
        cuerpo=json.loads(request.body)
        if not isinstance(cuerpo,dict) or not isinstance(cuerpo.get('mensaje'),str):
            raise ValueError('mensaje debe ser texto')
        mensaje=cuerpo['mensaje'].strip()
        if not 1<=len(mensaje)<=1000:
            raise ValueError('mensaje debe tener de 1 a 1000 caracteres')
    except (ValueError,UnicodeError) as error:
        return JsonResponse({'error':str(error)},status=400)
    try:
        intencion,confianza=clasificar(mensaje)
    except OSError:
        return JsonResponse({'error':'Ejecute el entrenamiento del asistente antes de consultar'},status=503)
    folio=extraer_folio(mensaje)
    if intencion=='fuera':
        respuesta='Esa pregunta queda fuera del dominio de entregas del tutorial.'
    elif confianza<.28:
        respuesta='No identifico con suficiente seguridad la solicitud. ¿Quieres consultar un folio o una recomendación?'
    elif intencion in ('seguimiento','explicacion'):
        pedido=Pedido.objects.filter(folio=folio).first() if folio else None
        if not folio:
            respuesta='Escribe el folio UUID completo del pedido para consultar su información.'
        elif not pedido:
            respuesta='No encontré ese folio. No voy a inventar su estado.'
        elif intencion=='seguimiento':
            respuesta=f'Pedido {pedido.folio}: {pedido.get_estado_display()}, medio {pedido.medio}, ETA {pedido.eta_minutos} minutos.'
        else:
            respuesta=f'Medio guardado: {pedido.medio}. Motivo registrado: {pedido.motivo_medio}.'
    elif intencion=='saludo':
        respuesta='Hola. Puedo orientar sobre entregas y consultar un pedido por su folio.'
    elif intencion=='catalogo':
        respuesta='La práctica contempla bicicleta, motocicleta, camioneta y dron. Disponibilidad sujeta a reglas del servidor.'
    elif intencion=='recomendacion':
        respuesta='Usa el formulario de recomendación con los datos del paquete. El recomendador, no este chat, decide el medio.'
    elif intencion=='explicacion':
        respuesta='Las reglas pueden descartar medios inviables; para explicar una operación necesito su folio.'
    else:
        respuesta='Esa pregunta queda fuera del dominio de entregas del tutorial.'
    return JsonResponse({'intencion':intencion,'respuesta':respuesta,'confianza':confianza})
