#!/bin/bash
# ------------------------------------------------------------------------------
# ARCHIVO: stop_redis.sh
# DESCRIPCIÓN: Script para detener el servidor Redis de forma controlada usando
#              el comando `redis-cli shutdown`. Verifica que el proceso haya sido
#              finalizado correctamente.
# AUTOR: Alejandro Castro Martínez
# FECHA DE CREACIÓN: 2025-04-17
# ÚLTIMA MODIFICACIÓN: 2025-04-17
# DEPENDENCIAS: Redis instalado en el sistema, redis-cli disponible en $PATH
# CONTEXTO:
#   - Proyecto DisPix: sistema distribuido para aplicar filtros a imágenes.
#   - Este script se ejecuta desde pub-sub/scripts para detener Redis localmente.
# ------------------------------------------------------------------------------

# Instrucción para detener Redis
echo "🛑 Deteniendo Redis..."
redis-cli shutdown

# Verifica si el proceso redis-server sigue activo
if ! pgrep redis-server > /dev/null; then
    echo "✅ Redis detenido correctamente."
else
    echo "❌ Redis sigue activo."
fi
