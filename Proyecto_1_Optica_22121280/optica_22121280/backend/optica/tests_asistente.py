import json
import uuid
from unittest.mock import Mock, patch
from django.core.management import call_command
from django.test import TestCase
from .asistente import AsistenteService
from .models import Orden, Paquete
from .tests import PERFIL


class AsistenteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('sembrar_demo', verbosity=0)

    def post(self, mensaje, **extra):
        return self.client.post('/api/asistente/', json.dumps({'mensaje': mensaje, **extra}), content_type='application/json')

    def crear_orden(self):
        r = self.client.post('/api/ordenes/', json.dumps(PERFIL), content_type='application/json', HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()))
        self.assertEqual(r.status_code, 201)
        return r.json()

    def test_modelo_real_saludo_y_fuera_dominio(self):
        for mensaje, intencion in [('hola', 'saludo'), ('quien gano el partido de futbol', 'fuera_dominio'), ('zzzxxyyqqq', 'fuera_dominio')]:
            d = self.post(mensaje).json()
            self.assertEqual(d['intencion'], intencion)
            self.assertTrue(d['respuesta'])
            self.assertTrue(d['version_asistente'].startswith('asistente-v1-'))
        self.assertEqual(Orden.objects.count(), 0)

    def test_catalogo_y_detalle_consultan_precio_actual(self):
        Paquete.objects.filter(codigo='antirreflejante').update(precio='1175.00', disponible=False)
        d = self.post('que paquetes ofrecen').json()
        self.assertEqual(d['intencion'], 'catalogo')
        p = next(p for p in d['datos']['paquetes'] if p['codigo'] == 'antirreflejante')
        self.assertEqual(p['precio'], '1175.00')
        self.assertFalse(p['disponible'])
        d = self.post('cuanto cuesta claridad').json()
        self.assertEqual(d['intencion'], 'detalle_producto')
        self.assertIn('1175.00', d['respuesta'])

    def test_seguimiento_real_snapshot_y_no_prediccion_nueva(self):
        orden = self.crear_orden()
        Paquete.objects.filter(codigo='esencial').update(precio='690.00')
        with patch('optica.services.OpticaService.recomendar', side_effect=AssertionError('No se debe recalcular un folio')):
            d = self.post('quiero rastrear mi orden ' + orden['folio']).json()
            self.assertEqual(d['intencion'], 'seguimiento')
            self.assertEqual(d['datos']['precio_confirmado'], '650.00')
            self.assertEqual(d['datos']['estado'], 'registrada')
            d = self.post('explica mi orden', folio=orden['folio']).json()
            self.assertEqual(d['intencion'], 'explicar_recomendacion')
            self.assertEqual(d['datos']['recomendacion'], orden['recomendacion'])
            self.assertIn('histórico', d['respuesta'])

    def test_folio_ausente_desconocido_invalido_y_ambiguo(self):
        self.assertEqual(self.post('quiero rastrear mi orden').json()['accion'], 'solicitar_folio')
        d = self.post('quiero rastrear mi orden', folio=str(uuid.uuid4())).json()
        self.assertFalse(d['datos']['encontrada'])
        self.assertEqual(self.post('hola', folio='123').status_code, 400)
        self.assertEqual(self.post('quiero rastrear ' + str(uuid.uuid4()), folio=str(uuid.uuid4())).status_code, 400)

    def test_recomendacion_delega_y_no_registra_orden(self):
        d = self.post('que paquete me recomiendas').json()
        self.assertEqual(d['accion'], 'abrir_recomendador')
        d = self.post('que paquete me recomiendas', perfil=PERFIL).json()
        self.assertEqual(d['datos']['recomendacion']['paquete']['codigo'], 'esencial')
        self.assertTrue(d['datos']['recomendacion']['corregido'])
        self.assertEqual(Orden.objects.count(), 0)

    def test_contexto_publico_con_fuente_no_inventa_horario(self):
        d = self.post('cual es el horario de atencion').json()
        self.assertEqual(d['intencion'], 'politicas')
        self.assertEqual(d['fuentes'][0]['id'], 'horario')
        self.assertIn('no existe un horario de atención confirmado', d['respuesta'])
        self.assertEqual(d['fuentes'][0]['origen'], 'ml/corpus_optica.json')

    def test_sin_fuente_y_baja_confianza_piden_aclaracion(self):
        clasificador = Mock()
        clasificador.clasificar.return_value = {'intencion': 'politicas', 'confianza': .9, 'version': 'test'}
        recuperador = Mock()
        recuperador.buscar.return_value = None
        d = AsistenteService(clasificador=clasificador, recuperador=recuperador).responder({'mensaje': 'tema sin documento'})
        self.assertEqual(d['fuentes'], [])
        self.assertIn('No encontré', d['respuesta'])
        clasificador.clasificar.return_value['intencion'] = 'aclaracion'
        d = AsistenteService(clasificador=clasificador).responder({'mensaje': 'ambiguo'})
        self.assertEqual(d['intencion'], 'aclaracion')
        self.assertEqual(d['datos'], {})

    def test_contrato_limites_y_metodos(self):
        for datos in [{}, [], {'mensaje': ''}, {'mensaje': 42}, {'mensaje': 'x' * 1001}, {'mensaje': 'hola', 'precio': 1}]:
            r = self.client.post('/api/asistente/', json.dumps(datos), content_type='application/json')
            self.assertEqual(r.status_code, 400)
        self.assertEqual(self.client.get('/api/asistente/').status_code, 405)
        self.assertEqual(self.client.post('/api/asistente/', '{}', content_type='text/plain').status_code, 415)
