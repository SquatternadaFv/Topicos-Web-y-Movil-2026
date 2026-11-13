import json
import os
from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from entregas.models import Pedido
from laboratorio.recomendadores import obtener_recomendador

PAQUETE={'distancia_km':12.64,'peso_kg':.31,'largo_cm':11.7,'ancho_cm':7.6,'alto_cm':10.6,
 'volumen_l':.94,'fragil':0,'refrigerado':0,'valor_declarado_mxn':4603,'hora_salida':3,
 'prioridad':'mismo_dia','zona_destino':'periferia','clima':'despejado','trafico':'medio'}


class BorradorTests(TestCase):
    def test_dos_clientes_no_se_mezclan_y_confirman_pedidos_distintos(self):
        otro=Client()
        self.client.get('/entregas/borrador/destino/',{'destino':'A'})
        otro.get('/entregas/borrador/destino/',{'destino':'B'})
        a=self.client.get('/entregas/borrador/confirmar/')
        b=otro.get('/entregas/borrador/confirmar/')
        self.assertEqual(a.status_code,201)
        self.assertEqual(b.status_code,201)
        self.assertEqual(Pedido.objects.get(folio=a.json()['folio']).destino,'A')
        self.assertEqual(Pedido.objects.get(folio=b.json()['folio']).destino,'B')
        self.assertEqual(self.client.get('/entregas/borrador/confirmar/').status_code,400)

    def test_confirmar_sin_destino_no_crea_pedido(self):
        self.assertEqual(self.client.get('/entregas/borrador/confirmar/').status_code,400)
        self.assertEqual(Pedido.objects.count(),0)

    @override_settings(DEMO_BORRADOR_GLOBAL=True)
    def test_contraejemplo_global_mezcla_usuarios(self):
        otro=Client()
        self.client.get('/entregas/borrador/destino/',{'destino':'A'})
        otro.get('/entregas/borrador/destino/',{'destino':'B'})
        self.assertEqual(self.client.get('/entregas/borrador/confirmar/').json()['destino'],'B')


class ApiTests(TestCase):
    def test_misma_vista_con_modelo_y_reglas_sin_modificar_http(self):
        for proveedor in ('arbol','reglas'):
            obtener_recomendador.cache_clear()
            with patch.dict(os.environ,{'RECOMENDADOR':proveedor}):
                r=self.client.post('/entregas/recomendar/',data=json.dumps(PAQUETE),content_type='application/json')
                self.assertEqual(r.status_code,200)
                self.assertNotEqual(r.json()['medio'],'dron')
        obtener_recomendador.cache_clear()

    def test_backend_valida_aunque_cliente_no_lo_haga(self):
        p={**PAQUETE};p.pop('peso_kg')
        self.assertEqual(self.client.post('/entregas/recomendar/',data=json.dumps(p),content_type='application/json').status_code,400)
        self.assertEqual(self.client.post('/entregas/recomendar/',data='[]',content_type='application/json').status_code,400)

    def test_preflight_flutter_local_y_rechazo_de_origen_ajeno(self):
        r=self.client.options('/entregas/recomendar/',HTTP_ORIGIN='http://localhost:19000')
        self.assertEqual(r.status_code,204)
        self.assertEqual(r['Access-Control-Allow-Origin'],'http://localhost:19000')
        r=self.client.options('/entregas/recomendar/',HTTP_ORIGIN='https://localhost.ejemplo.com')
        self.assertNotIn('Access-Control-Allow-Origin',r)

    def test_asistente_lee_folio_real_sin_inventar_estado(self):
        p=Pedido.objects.create(origen='Bodega',destino='Cliente',peso_kg=1,medio='moto',estado='EN_CAMINO')
        r=self.client.post('/entregas/asistente/',data=json.dumps({'mensaje':f'quiero rastrear el folio {p.folio}'}),content_type='application/json')
        self.assertEqual(r.status_code,200)
        self.assertIn(str(p.folio),r.json()['respuesta'])

    def test_asistente_no_acepta_mensaje_objeto(self):
        self.assertEqual(self.client.post('/entregas/asistente/',data='{"mensaje":{}}',content_type='application/json').status_code,400)
