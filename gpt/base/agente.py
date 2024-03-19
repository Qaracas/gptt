import json
from abc import ABC, abstractmethod


class Agente(ABC):
    """
    """
    def __init__(mi, url = None, cabeceras_http = None):
        mi.url = url
        mi.cabeceras_http = cabeceras_http

    @abstractmethod
    def __pregunta(mi, pregunta):
        """
        Envía al proveddor de IA remoto la pregunta
        """
        raise NotImplementedError("Este método debe ser implementado por una subclase.")

    @abstractmethod
    def __procesa_respuesta(mi, respuesta):
        """
        Devuelve procesada la respuesta obtenida anteriormente
        """
        raise NotImplementedError("Este método debe ser implementado por una subclase.")

    def pregunta(mi, pregunta):
        """
        Formula pregunta a la IA
        """
        respuesta = mi.__pregunta(pregunta)
        return mi.__procesa_respuesta(respuesta)
