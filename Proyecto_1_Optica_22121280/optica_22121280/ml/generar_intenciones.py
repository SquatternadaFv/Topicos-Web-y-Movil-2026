"""Dataset propio, redactado para el dominio comercial ficticio de Lúmina."""
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FRASES={
 'saludo':[
  'hola','buenos días','buenas tardes','buenas noches','hola lúmina','saludos','qué tal','hola asistente',
  'buen día quiero ayuda','hola necesito orientación','buenas óptica','hey hola','mucho gusto','hola de nuevo',
  'hola me puedes ayudar','quiero saludarte','hola buen día','saludos al asistente','hola cómo estás','buenas necesito ayuda'],
 'catalogo':[
  'qué paquetes ofrecen','quiero ver el catálogo','muéstrame todos los paquetes','cuáles son sus opciones','qué venden en lúmina',
  'lista de tratamientos disponibles','qué opciones de lentes tienen','puedo ver los productos','ver precios de los paquetes',
  'catálogo de paquetes de óptica','qué paquetes están activos','mostrar opciones comerciales','lista de paquetes y precios',
  'cuáles tratamientos manejan','enséñame el catálogo de la óptica','qué paquetes hay para comprar','tienen opciones de lentes',
  'dame la lista de productos','consultar catálogo completo','ver todas las opciones de la tienda'],
 'detalle_producto':[
  'cuánto cuesta claridad','qué incluye esencial','dame detalles de integral','quiero información de transición',
  'qué tratamientos incluye claridad','cuál es el precio de esencial','explícame el paquete premium','el fotocromático está disponible',
  'qué contiene el paquete antirreflejante','descripción del paquete esencial','detalles del producto claridad',
  'tienen disponible integral','consultar precio de transición','características del paquete premium','incluye fotocromático integral',
  'cuánto vale el paquete claridad','información específica de esencial','precio actual de integral',
  'qué lleva el tratamiento fotocromático','ficha del paquete transición'],
 'seguimiento':[
  'cómo va mi orden','consultar mi folio <folio>','rastrear solicitud <folio>','cuál es el estado de mi pedido',
  'ya registraron mi solicitud','buscar orden por folio','dónde consulto mi orden','ver mi solicitud registrada',
  'consulta el estado del folio <folio>','quiero rastrear mi orden','cómo está mi solicitud <folio>',
  'revisar estado de mi pedido <folio>','muéstrame mi orden <folio>','en qué estado está mi folio',
  'mi solicitud ya está registrada','buscar el pedido <folio>','seguimiento de mi solicitud','consulta de pedido por folio',
  'necesito el estado de mi orden','rastrear el folio de mi solicitud'],
 'explicar_recomendacion':[
  'por qué me salió esencial','explica la recomendación de mi folio','por qué el modelo eligió claridad',
  'por qué cambiaron mi paquete','cuál fue el motivo de la corrección','explica las reglas de mi orden <folio>',
  'por qué descartaron premium','por qué bajó la confianza de mi recomendación','explicación de mi resultado',
  'qué pasó con el ranking de mi solicitud','por qué terminé con esencial si el modelo dijo claridad',
  'quiero saber por qué recomendaron ese paquete','motivo guardado del folio <folio>','explica mi orden <folio>',
  'qué regla corrigió mi resultado','por qué mi presupuesto cambió la sugerencia','razón del paquete asignado',
  'explícame el resultado de mi orden','qué significa la corrección en mi folio','por qué esa alternativa fue descartada'],
 'recomendar':[
  'qué paquete me recomiendas','quiero una recomendación nueva','ayúdame a elegir lentes','necesito elegir un tratamiento',
  'tengo setecientos pesos qué me conviene','trabajo frente a pantalla qué paquete elijo','recomiéndame un paquete',
  'quiero usar el recomendador','calcular una sugerencia para mi perfil','cuál paquete se adapta a mi presupuesto',
  'elegir un paquete según mis preferencias','buscar una opción que me convenga','quisiera que el modelo evalúe mi perfil',
  'necesito una sugerencia comercial','quiero completar el perfil para recomendar','qué opción sería adecuada para mí',
  'obtener recomendación con mis datos','cómo encuentro mi paquete','quiero escoger entre los paquetes','puedes recomendarme una opción'],
 'politicas':[
  'cuál es el horario de atención','cómo limpio mis lentes','cómo se recoge una solicitud','qué significa una garantía en esta demo',
  'la óptica calcula mi graduación','el asistente puede darme un diagnóstico','cómo funciona el registro de una orden',
  'qué diferencia hay entre recomendación y receta','cómo cuido el armazón','cómo puedo consultar el horario',
  'cuándo atiende la tienda de demostración','cuáles son las condiciones del prototipo','información sobre retiro de solicitudes',
  'qué dice su guía de cuidados','qué puede y qué no puede hacer la aplicación','política de privacidad de la demostración',
  'qué datos personales guarda el prototipo','en qué consiste el proceso de atención','información de garantía y devoluciones',
  'quiero leer las políticas públicas'],
 'fuera_dominio':[
  'quién ganó el partido de fútbol','dame una receta de pastel','compra acciones de una empresa','cuéntame la historia de roma',
  'recomiéndame una película','cuánto es la raíz cuadrada de nueve','qué clima hay en marte','haz mi tarea de matemáticas',
  'qué celular debería comprar','quién es el presidente de otro país','escribe un poema sobre el mar','dime el precio del bitcoin',
  'cómo reparo el motor del coche','traduce una canción al inglés','cuál equipo ganó el torneo','enséñame a cocinar arroz',
  'quiero reservar un hotel','qué computadora compro para videojuegos','resuelve mi ecuación diferencial','dame noticias internacionales'],
}


def generar():
    ruta=ROOT/'datos/intenciones_optica.csv'
    ruta.parent.mkdir(parents=True,exist_ok=True)
    with ruta.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['id','texto','intencion','origen'])
        w.writeheader()
        for intencion,textos in FRASES.items():
            for i,texto in enumerate(textos,1):
                w.writerow({'id':f'{intencion}-{i:02d}','texto':texto,'intencion':intencion,'origen':'redacción académica propia asistida; sin conversaciones reales'})
    print(f'Dataset del asistente: {sum(map(len,FRASES.values()))} frases, {len(FRASES)} intenciones.')


if __name__=='__main__':generar()
