import json
from abc import ABC, abstractmethod


class Proveedor(ABC):

    def __init__(mi, solicitud, cabeceras_http):
        mi.solicitud_json = json.dumps(solicitud)
        mi.cabeceras_http = cabeceras_http

    @abstractmethod
    def __pregunta(mi, pregunta):
        """
        Envía al proveddor de IA remoto la pregunta que se le pasa como parámetro
        """
        pass

    @abstractmethod
    def __procesa_respuesta(mi, respuesta):
        """
        Devuelve procesada la respuesta que se le pasa como parámetro
        """
        pass

    def pregunta(mi, pregunta):
        """
        Formula pregunta a la IA
        """
        respuesta = mi.__pregunta(pregunta)
        return mi.__procesa_respuesta(respuesta)
