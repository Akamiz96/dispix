# subscriber_redis.py

import redis
import json
import os
import logging
import requests
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import base64
import numpy as np
import cv2

from utils.image_filters import aplicar_filtro

# Configurar directorio de logs
LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = os.path.join(LOG_DIR, "subscriber_log_" + datetime.now().strftime("%Y-%m-%d") + ".log")

# Configurar logger rotativo
handler = TimedRotatingFileHandler(
    filename=log_filename,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding='utf-8',
    delay=False
)
handler.suffix = "%Y-%m-%d"
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger("subscriber_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Conectar a Redis
r = redis.Redis(host="localhost", port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe("dispix-tasks")

# Dirección del servidor Flask
FLASK_SERVER_URL = "http://localhost:5000/result"

print("🟢 Esperando tareas en el canal 'dispix-tasks'...\n")

# Escuchar mensajes
for message in pubsub.listen():
    if message["type"] == "message":
        try:
            data = json.loads(message["data"])
            task_id = data.get("task_id", "N/A")
            block_id = data.get("block_id", "N/A")
            filtro = data.get("filter", "N/A")
            block_data = data.get("block_data", "")

            msg = f"📦 Bloque recibido -> Task: {task_id} | Block: {block_id} | Filtro: {filtro}"
            print(msg)
            logger.info(msg)

            # Decodificar imagen
            img_bytes = base64.b64decode(block_data)
            img_np = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

            # Aplicar filtro
            msg = f"🔄 Aplicando filtro: {filtro}"
            print(msg)
            logger.info(msg)
            img_procesado = aplicar_filtro(img, filtro)

            # Re-encodificar
            _, buffer = cv2.imencode(".png", img_procesado)
            block_data = base64.b64encode(buffer).decode("utf-8")

            # Enviar el bloque al servidor web
            response = requests.post(FLASK_SERVER_URL, json={
                "task_id": task_id,
                "block_id": block_id,
                "filter": filtro,
                "block_data": block_data
            })

            if response.status_code == 200:
                send_msg = f"✅ Bloque enviado al servidor Flask: {response.json()}"
                print(send_msg)
                logger.info(send_msg)
            else:
                error_msg = f"⚠️ Error al enviar al servidor Flask: {response.status_code}"
                print(error_msg)
                logger.warning(error_msg)

        except Exception as e:
            error_msg = f"❌ Error procesando mensaje: {e}"
            print(error_msg)
            logger.error(error_msg)
