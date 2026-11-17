from django.core.management.base import BaseCommand
from optica.models import Paquete

DATOS = [
    ('esencial', 'Esencial', 'Una opción accesible para el uso cotidiano.', '650.00', ['Lente monofocal base', 'Capa endurecida'], False),
    ('antirreflejante', 'Claridad', 'Paquete con tratamiento antirreflejante para preferencias de uso en interiores.', '1100.00', ['Lente monofocal base', 'Antirreflejante', 'Capa endurecida'], False),
    ('fotocromatico', 'Transición', 'Tratamiento fotocromático para quien prefiere adaptación de tono en exteriores.', '1800.00', ['Lente monofocal base', 'Fotocromático', 'Capa endurecida'], True),
    ('premium', 'Integral', 'Combina tratamientos del catálogo en un solo paquete.', '2400.00', ['Lente monofocal base', 'Antirreflejante', 'Fotocromático', 'Capa endurecida'], True),
]
class Command(BaseCommand):
    help = 'Crea o actualiza los cuatro paquetes académicos sin borrar órdenes.'
    def handle(self, *args, **options):
        for codigo, nombre, descripcion, precio, tratamientos, foto in DATOS:
            Paquete.objects.update_or_create(codigo=codigo, defaults=dict(nombre=nombre, descripcion=descripcion, precio=precio, tratamientos=tratamientos, fotocromatico=foto, disponible=True, activo=True))
        self.stdout.write(self.style.SUCCESS('Catálogo demo listo: 4 paquetes. No se borraron órdenes.'))
