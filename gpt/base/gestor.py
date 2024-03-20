from gpt.agentes.opengpts import *

class Gestor:
    """
    """
    def __init__(mi):
        mi.agentes_ia = {
            "opengpts" : OpenGpts()
        }

    def pregunta(mi, nombre_agente, pregunta):
        if nombre_agente in mi.agentes_ia:
            agente = mi.agentes_ia[nombre_agente]
            return agente.pregunta(pregunta)
        else:
            raise ExcepcionAgenteNoEncontrado(f"No se encontró el agente: '{nombre_agente}'.")

class ExcepcionAgenteNoEncontrado(Exception):
    def __init__(mi, mensaje):
        mi.mensaje = mensaje

    def __str__(mi):
        return mi.mensaje