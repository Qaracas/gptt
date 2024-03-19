import requests
import json
import re

from random import randrange
from gpt.base.agente import Agente

class OpenGpts(Agente):
    """
    """
    def __init__(mi):
        super().__init__(
                url = "https://opengpts-example-vz4y4ooboq-uc.a.run.app/runs/stream",
                cabeceras_http = {
                    "Authority"       : "opengpts-example-vz4y4ooboq-uc.a.run.app",
                    "Accept"          : "text/event-stream",
                    "Accept-Language" : "en-US,en;q=0.7",
                    "cache-Control"   : "no-cache",
                    "Content-Type"    : "application/json",
                    "Cookie"          : "opengpts_user_id=" + mi.__texto_aleatorio(36),
                    "Origin"          : "https://opengpts-example-vz4y4ooboq-uc.a.run.app",
                    "Pragma"          : "no-cache",
                    "Referer"         : "https://opengpts-example-vz4y4ooboq-uc.a.run.app/",
                    "Sec-Fetch-Site"  : "same-origin",
                    "Sec-GPC"         : "1",
                    "User-Agent"      : "Gptt/1.0"
                }
        )

    def __texto_aleatorio(mi, bulto):
        c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

        resultado = []
        for i in range(bulto):
            resultado.append(c[randrange(len(c))])

        return ''.join(resultado)

    def _Agente__pregunta(mi, pregunta):
        solicitud = {
            "input": [
                {
                    "content": pregunta,
                    "additional_kwargs": {},
                    "type": "human",
                    "example": False
                }
            ],
            "assistant_id": "bdc5981d-483e-44a8-bb42-1cced28c3574",
            "thread_id": ""
        }

        # Codifica solicitud a un texto JSON
        solicitud_json = json.dumps(solicitud)

        # Realiza la solicitud POST
        respuesta = requests.post(mi.url, data=solicitud_json, headers=mi.cabeceras_http)

        return respuesta.text

    def _Agente__procesa_respuesta(mi, respuesta):
        # Trae la respuesta final
        respuesta_json = re.findall(r'event: data\r\ndata: (.*)\r\n\r\nevent: end\r\n\r\n',
            respuesta)[0]
        # Descodifica a un objeto
        respuesta = json.loads(respuesta_json)

        return respuesta[1]["content"]
