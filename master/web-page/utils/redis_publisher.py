# utils/redis_publisher.py

import redis
import json
import base64
import cv2

# Configura la conexión con Redis
r = redis.Redis(host="localhost", port=6379, db=0)

def publish_block(task_id, block_id, filtro, block_image):
    """
    Publica una tarea de bloque en el canal Redis como JSON.
    - block_image: bloque de imagen (matriz OpenCV)
    """
    # Codificar bloque como base64 para que sea serializable
    _, buffer = cv2.imencode(".png", block_image)
    block_base64 = base64.b64encode(buffer).decode("utf-8")

    message = {
        "task_id": task_id,
        "block_id": block_id,
        "filter": filtro,
        "block_data": block_base64
    }

    r.publish("dispix-tasks", json.dumps(message))
