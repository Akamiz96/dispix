"""
------------------------------------------------------------------------------
ARCHIVO: subscriber_test.py
DESCRIPCIÓN: Script de prueba que actúa como suscriptor al canal Redis
             `dispix-tasks`. Escucha mensajes y los imprime para validar la
             correcta recepción desde un publisher.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: redis, json
CONTEXTO:
    - Proyecto DisPix.
    - Este script se ejecuta desde pub-sub/test-redis/ y se utiliza junto con
      publisher_test.py para validar la comunicación Redis pub/sub.
------------------------------------------------------------------------------
"""

import redis
import json

# Conexión al servidor Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Crear un objeto pubsub y suscribirse al canal
pubsub = r.pubsub()
pubsub.subscribe("dispix-tasks")

print("📡 [Subscriber] Escuchando en el canal 'dispix-tasks'...")

# Escuchar mensajes entrantes indefinidamente
for message in pubsub.listen():
    if message['type'] == 'message':
        # Decodificar y mostrar mensaje recibido
        data = json.loads(message['data'].decode())
        print(f"📥 [Subscriber] Mensaje recibido: {data}")
