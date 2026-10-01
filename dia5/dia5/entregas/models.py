import uuid

from django.db import models


class Pedido(models.Model):
    """El pedido no sabe de camionetas ni de IA: solo guarda su estado."""

    ESTADOS = [
        ("CREADO", "Creado"),
        ("EN_CAMINO", "En camino"),
        ("ENTREGADO", "Entregado"),
    ]

    folio = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    origen = models.CharField(max_length=200)
    destino = models.CharField(max_length=200)
    peso_kg = models.FloatField()
    medio = models.CharField(max_length=30, blank=True)
    motivo_medio = models.CharField(max_length=200, blank=True)
    eta_minutos = models.FloatField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="CREADO")
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.folio} ({self.estado})"


class Cobro(models.Model):
    """Cobro simulado: nace SIEMPRE junto con el pedido, o ninguno de
    los dos (Unit of Work en services.registrar_pedido)."""

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="cobro")
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    confirmado = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cobro {self.monto} de {self.pedido.folio}"
