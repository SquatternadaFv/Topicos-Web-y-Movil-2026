from django.contrib import admin
from .models import Paquete, Orden
@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'precio', 'disponible', 'activo']
    list_filter = ['disponible', 'activo']
    search_fields = ['codigo', 'nombre']
@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['folio', 'paquete', 'precio_confirmado', 'estado', 'creada']
    readonly_fields = ['folio', 'clave_idempotencia', 'paquete', 'entradas', 'resultado', 'precio_confirmado', 'creada']
    def has_add_permission(self, request):
        return False
