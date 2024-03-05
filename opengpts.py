import requests
import json

from random import randrange

def texto_aleatorio(bulto):
    c = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

    resultado = []
    for i in range(bulto):
        resultado.append(c[randrange(len(c))])

    return ''.join(resultado)



pregunta = "Por favor, define selva."

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

solicitud_json = json.dumps(solicitud)


# Encabezados de la solicitud
cabeceras_http = {
    "Authority"       : "opengpts-example-vz4y4ooboq-uc.a.run.app",
    "Accept"          : "text/event-stream",
    "Accept-Language" : "en-US,en;q=0.7",
    "cache-Control"   : "no-cache",
    "Content-Type"    : "application/json",
    "Cookie"          : "opengpts_user_id=" + texto_aleatorio(36),
    "Origin"          : "https://opengpts-example-vz4y4ooboq-uc.a.run.app",
    "Pragma"          : "no-cache",
    "Referer"         : "https://opengpts-example-vz4y4ooboq-uc.a.run.app/",
    "Sec-Fetch-Site"  : "same-origin",
    "Sec-GPC"         : "1",
    "User-Agent"      : "Gptt/1.0"
}

# Realizar la solicitud POST
url = "https://opengpts-example-vz4y4ooboq-uc.a.run.app/runs/stream"
respuesta = requests.post(url, data=solicitud_json, headers=cabeceras_http)

print(respuesta.text)