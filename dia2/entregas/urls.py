from django.urls import path

from entregas import views

urlpatterns = [
    path("pedidos/nuevo", views.crear_pedido, name="crear_pedido"),
    path("pedidos/<uuid:folio>", views.ver_pedido, name="ver_pedido"),
]
