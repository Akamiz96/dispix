#!/bin/bash

# Script para iniciar Redis en segundo plano

echo "🔄 Iniciando Redis..."
redis-server --daemonize yes

# Verificar si está corriendo
if pgrep redis-server > /dev/null; then
    echo "✅ Redis iniciado correctamente."
else
    echo "❌ No se pudo iniciar Redis."
fi
