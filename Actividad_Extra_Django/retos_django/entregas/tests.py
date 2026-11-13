from django.test import TestCase, override_settings
from entregas.reglas import elegir_medio, LIMITE_BICICLETA_KM
from entregas.models import Pedido
from entregas.services import registrar_pedido


class CotizacionTests(TestCase):
    def test_respuesta_correcta(self):
        respuesta = self.client.get('/entregas/cotizar/', {'km': 5, 'kg': 2})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['km'], 5.0)
        self.assertEqual(respuesta.json()['medio'], elegir_medio(5, 2)[0])

    def test_datos_invalidos_son_400_json(self):
        casos = [
            {'kg': '2'}, {'km': '5'}, {'km': '', 'kg': '2'},
            {'km': 'abc', 'kg': '2'}, {'km': '-1', 'kg': '2'},
            {'km': '1', 'kg': '-2'}, {'km': '1', 'kg': 'abc'},
            {'km': 'NaN', 'kg': '2'}, {'km': 'Infinity', 'kg': '2'},
            {'km': '1', 'kg': 'NaN'}, {'km': '1e999', 'kg': '2'},
        ]
        for parametros in casos:
            with self.subTest(parametros=parametros):
                respuesta = self.client.get('/entregas/cotizar/', parametros)
                self.assertEqual(respuesta.status_code, 400)
                self.assertIn('error', respuesta.json())

    def test_limites_y_prioridad(self):
        self.assertEqual(elegir_medio(LIMITE_BICICLETA_KM, 5)[0], 'bicicleta')
        self.assertEqual(elegir_medio(LIMITE_BICICLETA_KM + .1, 5)[0], 'moto')
        self.assertEqual(elegir_medio(1, 20)[0], 'moto')
        self.assertEqual(elegir_medio(1, 20.1)[0], 'camioneta')
        self.assertEqual(elegir_medio(15, 2)[0], 'moto')
        self.assertEqual(elegir_medio(15.1, 2)[0], 'camioneta')
        self.assertEqual(elegir_medio(0, 0)[0], 'bicicleta')

    def test_post_no_admitido(self):
        self.assertEqual(self.client.post('/entregas/cotizar/').status_code, 405)


class SesionTests(TestCase):
    def test_visitas_con_cookie(self):
        for esperado in range(1, 7):
            self.assertEqual(self.client.get('/entregas/visitas/').json()['visitas'], esperado)

    def test_folio_aislado_por_usuario(self):
        from django.test import Client
        otro = Client()
        self.client.get('/entregas/ultimo/', {'folio': 'ABC123'})
        otro.get('/entregas/ultimo/', {'folio': 'XYZ789'})
        self.assertEqual(self.client.get('/entregas/ultimo/ver/').json()['folio'], 'ABC123')
        self.assertEqual(otro.get('/entregas/ultimo/ver/').json()['folio'], 'XYZ789')

    def test_folio_vacio_es_400(self):
        self.assertEqual(self.client.get('/entregas/ultimo/').status_code, 400)

    @override_settings(DEMO_ULTIMO_GLOBAL=True)
    def test_modo_global_demostrativo(self):
        self.assertEqual(self.client.get('/entregas/ultimo/', {'folio': 'DEMO'}).json()['almacenamiento'], 'global')


class ProyectoAnteriorTests(TestCase):
    def test_pedido_existente_disponible_en_html_y_json(self):
        pedido = registrar_pedido('Bodega', 'Cliente', 2, 5)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(self.client.get(f'/pedidos/{pedido.folio}').status_code, 200)
        respuesta = self.client.get(f'/api/pedidos/{pedido.folio}')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['folio'], str(pedido.folio))
