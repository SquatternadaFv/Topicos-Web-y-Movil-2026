"""Único borde de persistencia usado por los servicios de negocio."""
from .models import Paquete, Orden

class CatalogoRepository:
    def listar(self, busqueda=''):
        qs = Paquete.objects.filter(activo=True)
        if busqueda:
            qs = qs.filter(nombre__icontains=busqueda)
        return list(qs)

    def obtener(self, codigo):
        return Paquete.objects.filter(codigo=codigo, activo=True).first()

class OrdenRepository:
    def por_clave(self, clave):
        return Orden.objects.select_related('paquete').filter(clave_idempotencia=clave).first()

    def por_folio(self, folio):
        return Orden.objects.select_related('paquete').filter(folio=folio).first()

    def crear(self, **datos):
        return Orden.objects.create(**datos)
