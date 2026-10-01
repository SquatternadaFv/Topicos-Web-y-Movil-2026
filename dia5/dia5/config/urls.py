from django.urls import include, path

# urls.py configura el despacho; el manejador HTTP y el resolver de
# Django cubren el papel de Front Controller. No escribimos otro.
urlpatterns = [
    path("", include("entregas.urls")),
]
