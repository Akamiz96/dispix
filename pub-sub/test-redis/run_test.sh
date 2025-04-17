#!/bin/bash

# Iniciar Redis
echo "🔄 Iniciando Redis..."
../scripts/start_redis.sh

# Esperar medio segundo
sleep 0.5

# Ejecutar el suscriptor en una terminal nueva
echo "📡 Abriendo Subscriber en una nueva terminal..."
gnome-terminal -- bash -c "source ../../venv/bin/activate && python ../subscriber_test.py; exec bash"

# Esperar para que el suscriptor se conecte
sleep 1

# Ejecutar el publisher
echo "📤 Ejecutando Publisher..."
python ../publisher_test.py
