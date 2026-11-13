import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from laboratorio.base import RAIZ, preparar, CAMPOS, es_posible
from laboratorio.recomendadores import (validar, RecomendadorArbol, RecomendadorReglas,
                                        RecomendadorConRespaldo, obtener_recomendador)

PAQUETE={'distancia_km':12.64,'peso_kg':.31,'largo_cm':11.7,'ancho_cm':7.6,'alto_cm':10.6,
 'volumen_l':.94,'fragil':0,'refrigerado':0,'valor_declarado_mxn':4603,'hora_salida':3,
 'prioridad':'mismo_dia','zona_destino':'periferia','clima':'despejado','trafico':'medio'}


class ContratosTests(unittest.TestCase):
    def test_tres_modelos_respetan_reglas_con_noche_lluvia_refrigeracion(self):
        for nombre in ('arbol','bosque','red'):
            for cambios in ({},{'clima':'lluvia'},{'refrigerado':1},{'zona_destino':'centro'}):
                p=validar({**PAQUETE,**cambios})
                with self.subTest(modelo=nombre,cambios=cambios):
                    r=RecomendadorArbol(nombre).sugerir(p)
                    self.assertTrue(es_posible(r['medio'],p))
                    self.assertNotEqual(r['medio'],'dron')

    def test_rechaza_numeros_no_finitos_y_ausencia_de_peso(self):
        for valor in (None,'abc',float('nan'),float('inf'),-1):
            with self.subTest(valor=valor),self.assertRaises(ValueError):
                validar({**PAQUETE,'peso_kg':valor})
        sin=dict(PAQUETE);del sin['peso_kg']
        with self.assertRaises(ValueError):validar(sin)

    def test_rechaza_hora_fraccionaria_y_volumen_inconsistente(self):
        for cambios in ({'hora_salida':3.5},{'volumen_l':1000},{'peso_kg':1001}):
            with self.assertRaises(ValueError):validar({**PAQUETE,**cambios})

    def test_respaldo_mantiene_contrato_y_explica_fallo(self):
        principal=RecomendadorArbol()
        with patch.object(principal,'sugerir',side_effect=RuntimeError('caída simulada')):
            r=RecomendadorConRespaldo(principal,RecomendadorReglas()).sugerir(PAQUETE)
        self.assertTrue(r['respaldo'])
        self.assertIn('RuntimeError',r['motivo'])
        self.assertTrue(es_posible(r['medio'],PAQUETE))

    def test_proveedor_reglas_por_configuracion(self):
        obtener_recomendador.cache_clear()
        with patch.dict(os.environ,{'RECOMENDADOR':'reglas'}):
            self.assertEqual(obtener_recomendador().sugerir(PAQUETE)['modelo'],'reglas')
        obtener_recomendador.cache_clear()

    def test_xml_traduce_vehicle_y_rechaza_desconocido(self):
        ruta=RAIZ/'dia3/entregas/ia.py'
        spec=importlib.util.spec_from_file_location('adaptador_dia3',ruta)
        mod=importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
        r=mod.AdaptadorXML(lambda peso,km:'<recommendation><vehicle>bike</vehicle><reason>corto</reason></recommendation>').sugerir(2,3)
        self.assertEqual(r.medio,'bicicleta')
        with self.assertRaises(ValueError):
            mod.AdaptadorXML(lambda peso,km:'<recommendation><vehicle>cohete</vehicle></recommendation>').sugerir(2,3)

    def test_estrategia_adicional_no_exige_cambiar_adaptador(self):
        # El cliente solo requiere planear; una nueva estrategia se registra en fábrica.
        ruta=RAIZ/'dia3/entregas/medios.py'
        spec=importlib.util.spec_from_file_location('estrategias_dia3',ruta)
        mod=importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
        class Triciclo:
            def planear(self,peso_kg,ctx):
                return mod.Plan.ok('triciclo',ctx.distancia_km/18*60) if peso_kg<=12 else mod.Plan.no_aplica()
        sys.path.insert(0,str(RAIZ/'dia3'))
        try:
            from entregas import fabrica
            with patch.dict(fabrica._CATALOGO, {'triciclo':Triciclo}):
                self.assertEqual(fabrica.crear_medio('triciclo').planear(8,mod.ContextoViaje(3)).medio,'triciclo')
                self.assertEqual(fabrica.crear_medio('bicicleta').planear(2,mod.ContextoViaje(3)).medio,'bicicleta')
        finally:
            sys.path.pop(0)


if __name__=='__main__':unittest.main()
