import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt


@require_GET
def formulario(request):
    return render(request, 'entregas/recomendador.html')


@csrf_exempt
@require_POST
def recomendar(request):
    from laboratorio.recomendadores import validar, obtener_recomendador
    try:
        cuerpo = json.loads(request.body)
        paquete = validar(cuerpo)
        modelo = cuerpo.get('modelo','arbol')
        if modelo not in ('arbol','bosque','red'):
            raise ValueError('Modelo desconocido.')
    except (ValueError, TypeError, UnicodeError) as error:
        return JsonResponse({'error':str(error)},status=400)
    resultado = obtener_recomendador(modelo).sugerir(paquete)
    return JsonResponse(resultado)
