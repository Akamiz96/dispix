"""
------------------------------------------------------------------------------
ARCHIVO: redis_publisher.py
DESCRIPCIÓN: Publica tareas individuales en el canal Redis del sistema DisPix.
             Cada tarea contiene un bloque de imagen codificado en base64,
             junto con el ID de tarea, ID de bloque y filtro a aplicar.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: redis, json, base64, opencv-python (cv2)
CONTEXTO:
    - Proyecto DisPix: sistema distribuido para procesamiento de imágenes.
    - Este módulo es invocado por el máster para publicar tareas que
      serán recibidas por los workers mediante suscripción al canal Redis.
------------------------------------------------------------------------------
"""

import redis
import json
import base64
import cv2

# Configura la conexión al servidor Redis (puerto y host por defecto)
r = redis.Redis(host="localhost", port=6379, db=0)

def publish_block(task_id, block_id, filtro, block_image):
    """
    Publica una tarea de bloque en el canal Redis como un mensaje JSON.

    Args:
        task_id (str): ID global de la tarea.
        block_id (str): ID del bloque (ej: '0_1') según su posición.
        filtro (str): Filtro a aplicar (ej: 'negative', 'blur', etc.).
        block_image (np.ndarray): Bloque de imagen en formato OpenCV.
    """

    # Codificar el bloque como imagen PNG en base64 para transmitirlo como texto
    _, buffer = cv2.imencode(".png", block_image)
    block_base64 = base64.b64encode(buffer).decode("utf-8")

    # Armar el mensaje en formato JSON
    message = {
        "task_id": task_id,
        "block_id": block_id,
        "filter": filtro,
        "block_data": block_base64
    }

    # Publicar mensaje al canal de tareas
    r.publish("dispix-tasks", json.dumps(message))
