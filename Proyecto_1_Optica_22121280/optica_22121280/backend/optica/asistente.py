"""Orquestación de P2: intención -> datos actuales, snapshot o contexto público."""
import re
import unicodedata
import uuid
from .clasificador_asistente import obtener_clasificador,PATRON_FOLIO
from .recuperacion import obtener_recuperador
from .repositories import CatalogoRepository,OrdenRepository
from .services import OpticaService,paquete_json
from .validation import ErrorDominio


def sin_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD',texto.casefold()) if unicodedata.category(c)!='Mn')


class AsistenteService:
    def __init__(self,clasificador=None,catalogo=None,ordenes=None,recuperador=None,recomendador=None):
        self.clasificador=clasificador
        self.catalogo=catalogo or CatalogoRepository()
        self.ordenes=ordenes or OrdenRepository()
        self.recuperador=recuperador
        self.recomendador=recomendador or OpticaService()

    def responder(self,datos):
        if not isinstance(datos,dict) or set(datos)-{'mensaje','folio','perfil'}:
            raise ErrorDominio('Envía un objeto con mensaje y, opcionalmente, folio o perfil.')
        mensaje=datos.get('mensaje')
        if not isinstance(mensaje,str) or not 1<=len(mensaje.strip())<=1000:
            raise ErrorDominio('mensaje debe ser texto de 1 a 1000 caracteres.')
        mensaje=mensaje.strip()
        encontrados={str(uuid.UUID(f)) for f in re.findall(PATRON_FOLIO,mensaje)}
        if datos.get('folio') is not None:
            try:encontrados.add(str(uuid.UUID(str(datos['folio']))))
            except (ValueError,TypeError,AttributeError):raise ErrorDominio('El folio debe ser un UUID válido.')
        if len(encontrados)>1:raise ErrorDominio('Indica un solo folio para evitar consultar otra solicitud.')
        folio=next(iter(encontrados),None)
        clasificacion=(self.clasificador or obtener_clasificador()).clasificar(mensaje)
        intencion=clasificacion['intencion']
        resultado={'intencion':intencion,'confianza_intencion':round(clasificacion['confianza'],6),
                   'version_asistente':clasificacion['version'],'fuentes':[],'accion':None,'datos':{}}
        if intencion=='saludo':
            respuesta='Hola. Soy el asistente de Lúmina. Puedo consultar catálogo, explicar una orden por su folio y orientarte al recomendador.'
        elif intencion=='catalogo':
            paquetes=[paquete_json(p) for p in self.catalogo.listar()]
            resultado['datos']['paquetes']=paquetes
            respuesta='Catálogo actual: '+('; '.join(f'{p["nombre"]}: ${p["precio"]} MXN'+(' (no disponible)' if not p['disponible'] else '') for p in paquetes) if paquetes else 'no hay paquetes activos.')
        elif intencion=='detalle_producto':
            consulta=sin_acentos(mensaje)
            candidatos=[p for p in self.catalogo.listar() if sin_acentos(p.nombre) in consulta or p.codigo in consulta]
            if not candidatos:
                respuesta='¿Qué paquete quieres consultar: Esencial, Claridad, Transición o Integral?'
            else:
                resultado['datos']['paquetes']=[paquete_json(p) for p in candidatos]
                respuesta='\n'.join(f'{p.nombre}: ${p.precio} MXN. {p.descripcion} Incluye: {", ".join(p.tratamientos)}. '+('Disponible.' if p.disponible else 'No disponible actualmente.') for p in candidatos)
        elif intencion in ('seguimiento','explicar_recomendacion'):
            if not folio:
                respuesta='Escribe el folio UUID completo en el mensaje o en el campo de referencia para consultar tu solicitud.'
                resultado['accion']='solicitar_folio'
            else:
                orden=self.ordenes.por_folio(folio)
                if orden is None:
                    respuesta='No encontré una solicitud con ese folio. Revisa el identificador; no se inventó un estado.'
                    resultado['datos']={'folio':folio,'encontrada':False}
                else:
                    r=orden.resultado
                    resultado['datos']={'folio':str(orden.folio),'encontrada':True,'estado':orden.estado,
                                       'precio_confirmado':str(orden.precio_confirmado),'recomendacion':r}
                    if intencion=='seguimiento':
                        respuesta=f'La solicitud {orden.folio} está {orden.estado}. Paquete registrado: {r["paquete"]["nombre"]}; total confirmado ${orden.precio_confirmado} MXN. Este estado no acredita fabricación o retiro.'
                    else:
                        respuesta=f'En la solicitud {orden.folio}, el modelo propuso {r["original"]} con confianza {r["confianza_original"]:.1%}. El paquete registrado fue {r["paquete"]["nombre"]}, con confianza del modelo {r["confianza"]:.1%}. {r["motivo"]} Se consultó el resultado histórico, sin volver a predecir.'
        elif intencion=='recomendar':
            if datos.get('perfil') is not None:
                r=self.recomendador.recomendar(datos['perfil'])
                resultado['datos']['recomendacion']=r
                respuesta=f'El recomendador del servidor propone {r["paquete"]["nombre"]}. {r["motivo"]} Puedes confirmar desde el flujo de recomendación; el chat no registró una orden.'
            else:
                respuesta='Para elegir un paquete hay que completar las cinco entradas del perfil. Abre Mi recomendación: el modelo de P1 y sus reglas calcularán el resultado. No deduzco un paquete solo de tu mensaje.'
                resultado['accion']='abrir_recomendador'
        elif intencion=='politicas':
            documento=(self.recuperador or obtener_recuperador()).buscar(mensaje)
            if documento:
                respuesta=documento['contenido']
                resultado['fuentes']=[{'id':documento['id'],'titulo':documento['titulo'],'version':documento['version'],
                                       'origen':'ml/corpus_optica.json','similitud':round(documento['similitud'],6)}]
            else:
                respuesta='No encontré una fuente pública que respalde esa respuesta. Aclara la pregunta; no se inventó una política.'
        elif intencion=='fuera_dominio':
            respuesta='Solo puedo orientar sobre el catálogo y las solicitudes de esta demostración de óptica. Esa pregunta está fuera de mi dominio.'
        else:
            respuesta='No identifico con suficiente seguridad lo que necesitas. ¿Quieres consultar catálogo, un folio, su explicación o abrir el recomendador?'
        return {**resultado,'respuesta':respuesta}
