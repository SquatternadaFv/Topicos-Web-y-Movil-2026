from django.urls import path
from . import views
urlpatterns = [
    path('salud/', views.salud),
    path('catalogo/', views.catalogo),
    path('catalogo/<slug:codigo>/', views.detalle),
    path('recomendaciones/', views.recomendar),
    path('ordenes/', views.registrar),
    path('ordenes/<uuid:folio>/', views.consultar),
    path('asistente/', views.asistente),
]
