from django.urls import include, path

# Este archivo, más el resolver que Django ya trae, ES el Front
# Controller: una sola entrada HTTP para todo el proyecto. No se
# construye ningún despachador casero al lado.
urlpatterns = [
    path("", include("entregas.urls")),
]
