import json
import uuid
from django.test import TestCase
from django.core.management import call_command
from .models import Orden, Paquete
from .services import OpticaService

PERFIL = {'horas_pantalla': 8, 'horas_exterior': 1, 'presupuesto': 700, 'uso_principal': 'oficina', 'prefiere_fotocromatico': False}

class FlujoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('sembrar_demo', verbosity=0)

    def post(self, ruta, datos, clave=None):
        headers = {'HTTP_IDEMPOTENCY_KEY': str(clave)} if clave else {}
        return self.client.post('/api/' + ruta + '/', json.dumps(datos), content_type='application/json', **headers)

    def test_catalogo_busqueda_y_detalle(self):
        self.assertEqual(len(self.client.get('/api/catalogo/').json()['resultados']), 4)
        self.assertEqual(len(self.client.get('/api/catalogo/?q=Claridad').json()['resultados']), 1)
        self.assertEqual(self.client.get('/api/catalogo/esencial/').json()['precio'], '650.00')
        self.assertEqual(self.client.get('/api/catalogo/no-existe/').status_code, 404)

    def test_modelo_real_corregido_presupuesto(self):
        r = self.post('recomendaciones', PERFIL)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['original'], 'antirreflejante')
        self.assertEqual(d['paquete']['codigo'], 'esencial')
        self.assertTrue(d['corregido'])
        self.assertAlmostEqual(sum(x['probabilidad'] for x in d['ranking']), 1, places=5)
        self.assertLessEqual(float(d['paquete']['precio']), PERFIL['presupuesto'])
        self.assertEqual(Orden.objects.count(), 0)

    def test_sin_correccion(self):
        d = self.post('recomendaciones', {**PERFIL, 'presupuesto': 3000}).json()
        self.assertFalse(d['corregido'])
        self.assertEqual(d['paquete']['codigo'], d['original'])

    def test_orden_folio_snapshot_e_idempotencia(self):
        clave = uuid.uuid4()
        a = self.post('ordenes', PERFIL, clave)
        b = self.post('ordenes', PERFIL, clave)
        self.assertEqual((a.status_code, b.status_code), (201, 200))
        self.assertEqual(a.json()['folio'], b.json()['folio'])
        self.assertEqual(Orden.objects.count(), 1)
        Paquete.objects.filter(codigo='esencial').update(precio='680.00')
        consulta = self.client.get('/api/ordenes/' + a.json()['folio'] + '/')
        self.assertEqual(consulta.json()['precio_confirmado'], '650.00')
        self.assertEqual(consulta.json()['recomendacion']['paquete']['precio'], '650.00')
        self.assertEqual(self.post('ordenes', {**PERFIL, 'presupuesto': 800}, clave).status_code, 409)

    def test_rechaza_precio_o_decision_del_cliente(self):
        r = self.post('ordenes', {**PERFIL, 'precio': 1, 'paquete': 'premium'}, uuid.uuid4())
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Orden.objects.count(), 0)

    def test_sin_opciones_no_guarda(self):
        for cambio in [{'presupuesto': 500}, {'presupuesto': 700, 'prefiere_fotocromatico': True}]:
            r = self.post('ordenes', {**PERFIL, **cambio}, uuid.uuid4())
            self.assertEqual(r.status_code, 422)
        self.assertEqual(Orden.objects.count(), 0)

    def test_disponibilidad(self):
        Paquete.objects.filter(codigo='antirreflejante').update(disponible=False)
        d = self.post('recomendaciones', {**PERFIL, 'presupuesto': 3000}).json()
        self.assertTrue(d['corregido'])
        self.assertNotEqual(d['paquete']['codigo'], 'antirreflejante')
        self.assertTrue(next(x for x in d['ranking'] if x['codigo'] == 'antirreflejante')['motivos'])

    def test_entradas_malformadas(self):
        for cambio in [{'horas_pantalla': True}, {'presupuesto': -1}, {'presupuesto': 650.001}, {'prefiere_fotocromatico': 'false'}, {'uso_principal': 'otro'}, {'horas_exterior': float('nan')}]:
            self.assertEqual(self.post('recomendaciones', {**PERFIL, **cambio}).status_code, 400)
        self.assertEqual(self.post('recomendaciones', []).status_code, 400)
        self.assertEqual(self.client.post('/api/recomendaciones/', '{', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/recomendaciones/', '{}', content_type='text/plain').status_code, 415)

    def test_metodo_cors_y_folio_inexistente(self):
        self.assertEqual(self.client.get('/api/recomendaciones/').status_code, 405)
        self.assertEqual(self.client.get(f'/api/ordenes/{uuid.uuid4()}/').status_code, 404)
        r = self.client.options('/api/ordenes/', HTTP_ORIGIN='http://localhost:5173')
        self.assertEqual(r['Access-Control-Allow-Origin'], 'http://localhost:5173')
        r = self.client.options('/api/ordenes/', HTTP_ORIGIN='https://ajeno.example')
        self.assertNotIn('Access-Control-Allow-Origin', r)

    def test_clave_obligatoria(self):
        self.assertEqual(self.post('ordenes', PERFIL).status_code, 400)
        self.assertEqual(Orden.objects.count(), 0)
