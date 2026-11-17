from decimal import Decimal, InvalidOperation

class ErrorDominio(Exception):
    def __init__(self, mensaje, status=400, campos=None):
        super().__init__(mensaje)
        self.status, self.campos = status, campos or {}

USOS = ('general', 'estudio', 'oficina', 'exterior')

def validar_entradas(datos):
    if not isinstance(datos, dict):
        raise ErrorDominio('El cuerpo debe ser un objeto JSON.')
    campos = {'horas_pantalla', 'horas_exterior', 'presupuesto', 'uso_principal', 'prefiere_fotocromatico'}
    errores, resultado = {}, {}
    for campo, minimo, maximo in [('horas_pantalla', 0, 16), ('horas_exterior', 0, 12), ('presupuesto', 300, 10000)]:
        valor = datos.get(campo)
        try:
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise InvalidOperation
            numero = Decimal(str(valor))
            if not numero.is_finite() or not minimo <= numero <= maximo:
                raise InvalidOperation
            if campo == 'presupuesto' and numero != numero.quantize(Decimal('.01')):
                raise InvalidOperation
            resultado[campo] = float(numero)
        except (InvalidOperation, ValueError, TypeError):
            errores[campo] = f'Debe ser un número entre {minimo} y {maximo}' + (' con máximo 2 decimales.' if campo == 'presupuesto' else '.')
    if datos.get('uso_principal') not in USOS:
        errores['uso_principal'] = 'Elige general, estudio, oficina o exterior.'
    else:
        resultado['uso_principal'] = datos['uso_principal']
    if type(datos.get('prefiere_fotocromatico')) is not bool:
        errores['prefiere_fotocromatico'] = 'Debe ser verdadero o falso.'
    else:
        resultado['prefiere_fotocromatico'] = datos['prefiere_fotocromatico']
    for campo in datos.keys() - campos:
        errores[campo] = 'Campo no permitido; el servidor calcula el resultado y el precio.'
    if errores:
        raise ErrorDominio('Revisa los campos del formulario.', campos=errores)
    return resultado
