import uuid
from django.db import models
from django.db.models import Q

class Paquete(models.Model):
    codigo = models.SlugField(unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=9, decimal_places=2)
    tratamientos = models.JSONField(default=list)
    fotocromatico = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['precio', 'codigo']
        constraints = [models.CheckConstraint(condition=Q(precio__gt=0), name='precio_positivo')]

    def __str__(self):
        return self.nombre

class Orden(models.Model):
    folio = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    clave_idempotencia = models.UUIDField(unique=True)
    paquete = models.ForeignKey(Paquete, on_delete=models.PROTECT)
    entradas = models.JSONField()
    resultado = models.JSONField()
    precio_confirmado = models.DecimalField(max_digits=9, decimal_places=2)
    creada = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=30, default='registrada')

    class Meta:
        ordering = ['-creada']
