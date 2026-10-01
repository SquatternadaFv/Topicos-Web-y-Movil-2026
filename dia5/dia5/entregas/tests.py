"""Pruebas del contrato del día 5 y de la continuidad del día 4."""

import uuid
from unittest.mock import patch

from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from entregas.models import Cobro, Pedido
from entregas.services import registrar_pedido


class ConsultaPedidoTests(TestCase):
    def setUp(self):
        # Estado y ETA distintos del alta inicial: los GET deben leer la BD.
        self.pedido = Pedido.objects.create(
            origen="Bodega", destino="Cliente", peso_kg=1.5,
            medio="dron", estado="EN_CAMINO", eta_minutos=17.5,
        )
        self.html = reverse("ver_pedido", kwargs={"folio": self.pedido.folio})
        self.api = reverse("ver_pedido_json", kwargs={"folio": self.pedido.folio})

    def test_html_y_json_del_mismo_folio_con_una_consulta_cada_uno(self):
        with self.assertNumQueries(1):
            html = self.client.get(self.html)
        with self.assertNumQueries(1):
            api = self.client.get(self.api)
        self.assertEqual(html.status_code, 200)
        self.assertEqual(api.status_code, 200)
        self.assertEqual(api.headers["Content-Type"], "application/json")
        self.assertEqual(api.json(), {
            "folio": str(self.pedido.folio), "estado": "EN_CAMINO", "eta": 17.5,
        })
        self.assertEqual(str(html.context["folio"]), api.json()["folio"])
        self.assertEqual(html.context["estado"], "En camino")
        self.assertEqual(html.context["eta"], api.json()["eta"])
        self.assertContains(html, self.api)

    def test_consultas_no_invocan_la_ia_ni_replanean(self):
        with patch("entregas.ia.IA_DISPONIBLE", False), patch(
            "entregas.ia.AdaptadorIAFalsa.sugerir",
            side_effect=AssertionError("Una consulta no debe llamar a la IA"),
        ), patch(
            "entregas.services.crear_medio",
            side_effect=AssertionError("Una consulta no debe crear estrategias"),
        ):
            self.assertEqual(self.client.get(self.html).status_code, 200)
            self.assertEqual(self.client.get(self.api).json()["eta"], 17.5)

    def test_folio_inexistente_devuelve_404(self):
        folio = uuid.uuid4()
        self.assertEqual(self.client.get(f"/pedidos/{folio}").status_code, 404)
        respuesta = self.client.get(f"/api/pedidos/{folio}")
        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json(), {"error": "Pedido no encontrado"})

    def test_metodos_distintos_de_get_no_modifican_el_pedido(self):
        for ruta in (self.html, self.api):
            respuesta = self.client.post(ruta)
            self.assertEqual(respuesta.status_code, 405)
            self.assertEqual(respuesta.headers["Allow"], "GET")
        self.assertEqual(Pedido.objects.count(), 1)

    def test_eta_sin_estimacion_se_serializa_como_null(self):
        self.pedido.eta_minutos = None
        self.pedido.save(update_fields=["eta_minutos"])
        self.assertIsNone(self.client.get(self.api).json()["eta"])

    def test_reporte_de_20_pedidos_ejecuta_una_consulta(self):
        Pedido.objects.bulk_create([
            Pedido(origen="Bodega", destino=f"Cliente {i}", peso_kg=1,
                   medio="bicicleta", eta_minutos=20)
            for i in range(19)
        ])
        with self.assertNumQueries(1):
            respuesta = self.client.get(reverse("reporte_pedidos"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context["pedidos"]), 20)


class AltaPedidoTests(TestCase):
    datos = {"origen": "Bodega", "destino": "Cliente",
             "peso_kg": "1.5", "distancia_km": "8"}

    def test_post_prg_y_recarga_sin_nuevo_pedido_ni_cobro(self):
        for ruta in ("/pedidos", "/pedidos/nuevo"):
            respuesta = self.client.post(ruta, self.datos)
            self.assertEqual(respuesta.status_code, 302)
            pedido = Pedido.objects.latest("creado_en")
            self.assertEqual(respuesta.headers["Location"],
                             reverse("ver_pedido", kwargs={"folio": pedido.folio}))
            cantidad = Pedido.objects.count()
            for _ in range(2):
                self.assertEqual(self.client.get(respuesta.headers["Location"]).status_code, 200)
            self.assertEqual(Pedido.objects.count(), cantidad)
            self.assertEqual(Cobro.objects.count(), cantidad)
            self.assertEqual(pedido.eta_minutos, 12.0)

    def test_alta_con_ia_apagada_usa_fallback(self):
        with patch("entregas.ia.IA_DISPONIBLE", False):
            respuesta = self.client.post("/pedidos", self.datos)
        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.medio, "camioneta")
        self.assertEqual(pedido.motivo_medio, "IA_NO_DISPONIBLE_FALLBACK")
        self.assertEqual(Cobro.objects.count(), 1)

    def test_fallo_del_cobro_revierte_el_pedido_y_no_avisa(self):
        with self.captureOnCommitCallbacks(execute=True) as callbacks, patch(
            "entregas.services._avisar"
        ) as avisar, patch(
            "entregas.services.Cobro.objects.create", side_effect=RuntimeError("Cobro fallido")
        ):
            with self.assertRaises(RuntimeError):
                registrar_pedido("Bodega", "Cliente", 1.5, 8)
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(Cobro.objects.count(), 0)
        self.assertEqual(callbacks, [])
        avisar.assert_not_called()


class AvisoTrasCommitTests(TransactionTestCase):
    def test_aviso_fallido_despues_del_commit_conserva_alta_y_redireccion(self):
        observado = []

        def fallar_aviso(pedido):
            # TransactionTestCase permite observar un commit real, no simulado.
            from django.db import connection
            observado.append((connection.in_atomic_block,
                              Pedido.objects.filter(pk=pedido.pk).exists(),
                              Cobro.objects.filter(pedido=pedido).exists()))
            raise RuntimeError("Aviso fallido")

        with patch("entregas.services._avisar", side_effect=fallar_aviso), self.assertLogs(
            "django.db.backends.base", level="ERROR"
        ):
            respuesta = self.client.post("/pedidos", AltaPedidoTests.datos)
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(observado, [(False, True, True)])
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(Cobro.objects.count(), 1)
