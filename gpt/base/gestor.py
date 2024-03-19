from gpt.agentes.opengpts import OpenGpts

class Gestor:

    def __init__(mi):
        mi.proveedores_ia = {
            "opengpts" : OpenGpts()
        }

    def pregunta(mi, nombre_proveedor, pregunta):
        if nombre_proveedor in mi.proveedores_ia:
            proveedor = mi.proveedores_ia[nombre_proveedor]
            return proveedor.pregunta(pregunta)
        else:
            return f"No se encontró proveedor '{nombre_proveedor}'."
