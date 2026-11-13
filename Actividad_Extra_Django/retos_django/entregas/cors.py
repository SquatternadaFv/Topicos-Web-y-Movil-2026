"""CORS de laboratorio para Flutter web local; no es autenticación."""
from urllib.parse import urlparse
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class CorsLocal:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self,request):
        api=request.path in ('/entregas/recomendar/','/entregas/asistente/')
        origen=request.headers.get('Origin','')
        parsed=urlparse(origen)
        permitido=parsed.scheme in ('http','https') and parsed.hostname in ('localhost','127.0.0.1')
        response=HttpResponse(status=204) if api and request.method=='OPTIONS' and permitido else self.get_response(request)
        if api and permitido:
            response['Access-Control-Allow-Origin']=origen
            response['Access-Control-Allow-Methods']='GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers']='Content-Type'
            patch_vary_headers(response,['Origin'])
        return response
