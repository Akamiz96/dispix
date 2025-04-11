import redis
import json

# Conexión a Redis local
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Mensaje de prueba
message = {
    "block_id": "0_0",
    "filter": "blur",
    "info": "Mensaje de prueba desde el máster"
}

# Publicar en el canal
redis_client.publish("dispix-tasks", json.dumps(message))
print("✅ Mensaje publicado en 'dispix-tasks'")
