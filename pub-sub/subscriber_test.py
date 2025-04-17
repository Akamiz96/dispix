import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe("dispix-tasks")

print("📡 [Subscriber] Escuchando en el canal 'dispix-tasks'...")

for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'].decode())
        print(f"📥 [Subscriber] Mensaje recibido: {data}")
