import redis
import json
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

print("📤 [Publisher] Iniciando publicación de bloques...")

for i in range(1, 6):  # simular 5 bloques
    message = {
        "block_id": f"{i}_0",
        "filter": "blur",
        "info": f"Bloque {i} enviado por Publisher"
    }
    redis_client.publish("dispix-tasks", json.dumps(message))
    print(f"📤 [Publisher] Mensaje publicado: {message}")
    time.sleep(0.5)  # pausa para ver mensajes en tiempo real

print("✅ [Publisher] Publicación finalizada.")
