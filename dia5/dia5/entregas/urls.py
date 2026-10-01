from django.urls import path

from entregas import views

urlpatterns = [
    path("entregas/hola/", views.hola, name="hola"),
    path("pedidos", views.crear_pedido, name="pedidos"),
    path("pedidos/nuevo", views.crear_pedido, name="crear_pedido"),
    path("pedidos/<uuid:folio>", views.ver_pedido, name="ver_pedido"),
    path("api/pedidos/<uuid:folio>", views.ver_pedido_json, name="ver_pedido_json"),
    path("reporte", views.reporte_pedidos, name="reporte_pedidos"),
]
