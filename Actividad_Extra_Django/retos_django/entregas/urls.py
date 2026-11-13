from django.urls import path

from entregas import views
from entregas import retos_views as retos
from entregas import modelo_views
from entregas import asistente_views

urlpatterns = [
    path('entregas/asistente/', asistente_views.asistente, name='asistente'),
    path('entregas/borrador/destino/', retos.borrador_destino, name='borrador_destino'),
    path('entregas/borrador/confirmar/', retos.borrador_confirmar, name='borrador_confirmar'),
    path('entregas/pedidos/', retos.pedidos_demo, name='pedidos_demo'),
    path('entregas/pedidos-mal/', retos.pedidos_demo, {'malo':True}, name='pedidos_demo_mal'),
    path('entregas/modelo/', modelo_views.formulario, name='modelo_formulario'),
    path('entregas/recomendar/', modelo_views.recomendar, name='recomendar'),
    path('entregas/hola/', retos.hola, name='hola'),
    path('entregas/estado/', retos.estado, name='estado'),
    path('entregas/cotizar/', retos.cotizar, name='cotizar'),
    path('entregas/cotizador/', retos.cliente_web, name='cotizador'),
    path('entregas/visitas/', retos.visitas, name='visitas'),
    path('entregas/visitas-mal/', retos.visitas_mal, name='visitas_mal'),
    path('entregas/ultimo/', retos.ultimo, name='ultimo'),
    path('entregas/ultimo/ver/', retos.ver_ultimo, name='ver_ultimo'),
    path('entregas/ultimo-mal/', retos.ultimo_mal, name='ultimo_mal'),
    path('entregas/ultimo-mal/ver/', retos.ver_ultimo_mal, name='ver_ultimo_mal'),
    path("pedidos/nuevo", views.crear_pedido, name="crear_pedido"),
    path("pedidos/<uuid:folio>", views.ver_pedido, name="ver_pedido"),
    path("api/pedidos/<uuid:folio>", views.ver_pedido_json, name="ver_pedido_json"),
    path("reporte", views.reporte_pedidos, name="reporte_pedidos"),
]
