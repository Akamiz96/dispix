"""
------------------------------------------------------------------------------
ARCHIVO: publisher_test.py
DESCRIPCIÓN: Script de prueba para simular la publicación de mensajes en el
             canal Redis `dispix-tasks`. Emite bloques ficticios con filtro
             asignado para verificar la recepción por parte del subscriber.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: redis, json, time
CONTEXTO:
    - Proyecto DisPix.
    - Este script se encuentra en pub-sub/test-redis/ y permite probar la
      comunicación pub/sub sin necesidad de levantar el sistema completo.
------------------------------------------------------------------------------
"""

import redis
import json
import time

# Conexión al servidor Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

print("📤 [Publisher] Iniciando publicación de bloques...")

# Simula la publicación de 5 bloques
for i in range(1, 6):
    message = {
        "block_id": f"{i}_0",
        "filter": "blur",
        "info": f"Bloque {i} enviado por Publisher"
    }
    # Publicar el mensaje como string JSON
    redis_client.publish("dispix-tasks", json.dumps(message))
    print(f"📤 [Publisher] Mensaje publicado: {message}")
    time.sleep(0.5)  # Espera entre envíos para simular tiempo real

print("✅ [Publisher] Publicación finalizada.")
