"""Recorrido de Flutter web compilado con API real y capturas de Chrome.

Requiere la demo activa y `pip install playwright`. No instala navegadores.
Ejemplo Windows: python scripts/capturar_navegador.py
Esta comprobación registra una solicitud de demostración.
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidencias'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chrome', default=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    parser.add_argument('--url', default='http://127.0.0.1:5173')
    parser.add_argument('--salida', type=Path, default=OUT)
    parser.add_argument('--con-asistente', action='store_true')
    args = parser.parse_args()
    salida = args.salida.resolve()
    salida.mkdir(parents=True, exist_ok=True)
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chrome, headless=True)
        page = browser.new_page(viewport={'width': 1100, 'height': 1050})
        page.on('pageerror', lambda error: errors.append(str(error)))

        def snap(name):
            page.wait_for_timeout(350)
            page.screenshot(path=str(salida / name))

        def response_for(path):
            return page.expect_response(lambda r: r.url.endswith(path) and r.request.method == 'POST')

        def escribir(campo, texto):
            # Flutter sincroniza foco/selección con su canal de texto en otro frame.
            # Esperar ese frame evita escribir sobre un controlador aún sin foco.
            campo.click()
            page.wait_for_timeout(200)
            campo.fill(texto)
            page.wait_for_timeout(150)
            campo.press('Tab')

        try:
            page.goto(args.url)
            # Flutter ofrece una capa semántica para lectores y automatización.
            page.locator('flt-semantics-placeholder').wait_for(state='attached')
            page.locator('flt-semantics-placeholder').evaluate('(element) => element.click()')
            expect(page.get_by_role('button', name='Encontrar mi paquete')).to_be_visible()
            expect(page.get_by_role('button', name='Claridad', exact=False)).to_be_visible()
            snap('10_chrome_inicio.png')
            page.get_by_role('button', name='Encontrar mi paquete').click()
            expect(page.get_by_role('textbox', name='Presupuesto máximo (MXN)', exact=True)).to_be_visible()
            snap('11_chrome_formulario.png')
            with response_for('/api/recomendaciones/') as response:
                page.get_by_role('button', name='Obtener recomendación', exact=True).click()
            assert response.value.status == 200
            recommendation = response.value.json()
            assert recommendation['original'] == 'antirreflejante'
            assert recommendation['paquete']['codigo'] == 'esencial'
            assert recommendation['corregido'] is True
            expect(page.get_by_text('Ajustado por reglas comerciales', exact=False)).to_be_visible()
            snap('12_chrome_recomendacion.png')
            page.mouse.wheel(0, 650)
            snap('13_chrome_reglas.png')
            page.get_by_role('button', name='Registrar solicitud y obtener folio', exact=True).click()
            with response_for('/api/ordenes/') as response:
                page.get_by_role('button', name='Confirmar registro', exact=True).click()
            assert response.value.status == 201
            order = response.value.json()
            expect(page.get_by_role('heading', name='Solicitud registrada', exact=True)).to_be_visible()
            snap('14_chrome_folio.png')

            page.get_by_role('button', name='Back', exact=True).click()
            page.get_by_role('tab', name='Consultar folio', exact=True).click()
            escribir(page.get_by_role('textbox', name='Folio de la solicitud', exact=True), order['folio'])
            with page.expect_response(lambda r: r.url.endswith('/api/ordenes/' + order['folio'] + '/') and r.request.method == 'GET') as response:
                page.get_by_role('button', name='Consultar solicitud', exact=True).click()
            assert response.value.status == 200
            assert response.value.json()['recomendacion'] == order['recomendacion']
            expect(page.get_by_role('heading', name='Detalle de la solicitud', exact=True)).to_be_visible()
            snap('15_chrome_consulta.png')

            page.get_by_role('button', name='Back', exact=True).click()
            page.get_by_role('tab', name='Mi recomendación', exact=True).click()
            escribir(page.get_by_role('textbox', name='Presupuesto máximo (MXN)', exact=True), '500')
            with response_for('/api/recomendaciones/') as response:
                page.get_by_role('button', name='Obtener recomendación', exact=True).click()
            assert response.value.status == 422
            expect(page.get_by_text('No hay un paquete disponible', exact=False)).to_be_visible()
            snap('16_chrome_sin_opciones.png')
            page.get_by_role('tab', name='Catálogo', exact=True).click()
            expect(page.get_by_role('button', name='Encontrar mi paquete')).to_be_visible()
            page.set_viewport_size({'width': 390, 'height': 844})
            snap('17_chrome_movil.png')
            assistant = []
            if args.con_asistente:
                page.set_viewport_size({'width': 1100, 'height': 1050})
                page.get_by_role('tab', name='Asistente', exact=True).click()

                def preguntar(mensaje, intencion, captura):
                    escribir(page.get_by_role('textbox', name='Mensaje', exact=True), mensaje)
                    with response_for('/api/asistente/') as response:
                        page.get_by_role('button', name='Enviar mensaje', exact=False).click()
                    assert response.value.status == 200
                    data = response.value.json()
                    assert data['intencion'] == intencion, data
                    # SelectionArea expone la burbuja como grupo accesible: título + texto.
                    nombre = 'Asistente Lúmina ' + ' '.join(data['respuesta'].split())
                    expect(page.get_by_role('group', name=nombre, exact=False).last).to_be_visible()
                    assert response.value.request.post_data_json['mensaje'] == mensaje
                    assistant.append({'mensaje': mensaje, 'resultado': data})
                    snap(captura)
                    return data

                preguntar('hola', 'saludo', '20_chat_saludo.png')
                preguntar('qué paquetes ofrecen', 'catalogo', '21_chat_catalogo.png')
                escribir(page.get_by_role('textbox', name='Folio de referencia (opcional)', exact=False), order['folio'])
                d = preguntar('quiero rastrear mi orden', 'seguimiento', '22_chat_folio_real.png')
                assert d['datos']['folio'] == order['folio']
                assert d['datos']['precio_confirmado'] == order['precio_confirmado']
                d = preguntar('explica mi orden', 'explicar_recomendacion', '23_chat_explicacion.png')
                assert d['datos']['recomendacion'] == order['recomendacion']
                d = preguntar('cuál es el horario de atención', 'politicas', '24_chat_dominio_fuente.png')
                assert d['fuentes'][0]['id'] == 'horario'
                preguntar('quién ganó el partido de fútbol', 'fuera_dominio', '25_chat_fuera_dominio.png')
                d = preguntar('qué paquete me recomiendas', 'recomendar', '26_chat_abrir_recomendador.png')
                assert d['accion'] == 'abrir_recomendador'
                page.get_by_role('button', name='Completar mi perfil', exact=True).click()
                expect(page.get_by_role('textbox', name='Presupuesto máximo (MXN)', exact=True)).to_be_visible()
                page.get_by_role('tab', name='Asistente', exact=True).click()
                page.set_viewport_size({'width': 390, 'height': 844})
                snap('27_chat_movil.png')
            assert not errors, errors
            evidence = {'origen': 'Chrome headless / Flutter web compilado / Django y modelo reales',
                        'navegador': browser.version, 'folio': order['folio'],
                        'recomendacion': recommendation, 'orden': order,
                        'consulta_identica': True, 'sin_opciones_http': 422,
                        'errores_javascript': errors, 'asistente': assistant}
            (salida / 'recorrido_chrome.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({'estado': 'correcto', 'folio': order['folio'], 'capturas': 16 if args.con_asistente else 8, 'errores_javascript': errors}, ensure_ascii=False))
        except Exception:
            snap('chrome_revision_fallo.png')
            print(page.locator('body').aria_snapshot())
            raise
        finally:
            browser.close()


if __name__ == '__main__':
    main()
