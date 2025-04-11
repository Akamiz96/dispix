#!/bin/bash

# Script para detener Redis

echo "🛑 Deteniendo Redis..."
redis-cli shutdown

# Verificar si se detuvo
if ! pgrep redis-server > /dev/null; then
    echo "✅ Redis detenido correctamente."
else
    echo "❌ Redis sigue activo."
fi
