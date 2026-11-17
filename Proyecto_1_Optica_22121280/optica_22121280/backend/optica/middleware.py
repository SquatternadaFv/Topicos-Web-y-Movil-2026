from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers

class CorsLocalMiddleware:
    """Orígenes explícitos; la API pública de demo no utiliza cookies de sesión."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get('Origin')
        response = HttpResponse(status=204) if request.method == 'OPTIONS' and request.path.startswith('/api/') else self.get_response(request)
        if origin in settings.CORS_ALLOWED_ORIGINS and request.path.startswith('/api/'):
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Idempotency-Key'
        patch_vary_headers(response, ['Origin'])
        return response
