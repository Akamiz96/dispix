"""
------------------------------------------------------------------------------
ARCHIVO: subscriber_redis.py
DESCRIPCIÓN: Worker principal del sistema DisPix. Se suscribe al canal Redis
             'dispix-tasks', recibe bloques de imagen junto con el filtro a
             aplicar, los procesa y luego envía el resultado de vuelta al
             servidor Flask mediante una solicitud HTTP POST.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: redis, json, logging, requests, base64, numpy, opencv-python
CONTEXTO:
    - Proyecto DisPix: sistema distribuido de procesamiento de imágenes.
    - Este archivo se ejecuta en cada worker y es responsable de recibir,
      procesar y reenviar cada bloque.
------------------------------------------------------------------------------
"""

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

# -----------------------------
# Configuración del Logger
# -----------------------------
LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = os.path.join(LOG_DIR, "subscriber_log_" + datetime.now().strftime("%Y-%m-%d") + ".log")

# Crear logger rotativo diario
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

# -----------------------------
# Conexión a Redis
# -----------------------------
r = redis.Redis(host="localhost", port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe("dispix-tasks")

# -----------------------------
# Dirección del servidor Flask
# -----------------------------
FLASK_SERVER_URL = "http://localhost:5000/result"

print("🟢 Esperando tareas en el canal 'dispix-tasks'...\n")

# -----------------------------
# Bucle principal del worker
# -----------------------------
for message in pubsub.listen():
    if message["type"] == "message":
        try:
            # -------------------------
            # Decodificar mensaje JSON
            # -------------------------
            data = json.loads(message["data"])
            task_id = data.get("task_id", "N/A")
            block_id = data.get("block_id", "N/A")
            filtro = data.get("filter", "N/A")
            block_data = data.get("block_data", "")

            msg = f"📦 Bloque recibido -> Task: {task_id} | Block: {block_id} | Filtro: {filtro}"
            print(msg)
            logger.info(msg)

            # -------------------------
            # Decodificar imagen base64
            # -------------------------
            img_bytes = base64.b64decode(block_data)
            img_np = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

            # -------------------------
            # Aplicar el filtro indicado
            # -------------------------
            msg = f"🔄 Aplicando filtro: {filtro}"
            print(msg)
            logger.info(msg)
            img_procesado = aplicar_filtro(img, filtro)

            # -------------------------
            # Re-encodificar imagen
            # -------------------------
            _, buffer = cv2.imencode(".png", img_procesado)
            block_data = base64.b64encode(buffer).decode("utf-8")

            # -------------------------
            # Enviar bloque procesado al máster
            # -------------------------
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
