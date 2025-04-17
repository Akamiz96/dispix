#!/bin/bash
# ------------------------------------------------------------------------------
# ARCHIVO: start_redis.sh
# DESCRIPCIÓN: Script para iniciar el servidor Redis en segundo plano. Verifica
#              si el proceso fue lanzado correctamente y muestra un mensaje de estado.
# AUTOR: Alejandro Castro Martínez
# FECHA DE CREACIÓN: 2025-04-17
# ÚLTIMA MODIFICACIÓN: 2025-04-17
# DEPENDENCIAS: Redis instalado y disponible en $PATH
# CONTEXTO:
#   - Proyecto DisPix: Sistema distribuido para procesamiento de imágenes.
#   - Este script se ejecuta desde pub-sub/scripts para facilitar el arranque
#     local de Redis durante pruebas y desarrollo.
# ------------------------------------------------------------------------------

# Mensaje inicial
echo "🔄 Iniciando Redis..."

# Inicia el servidor Redis en segundo plano (modo daemon)
redis-server --daemonize yes

# Verifica si Redis está en ejecución
if pgrep redis-server > /dev/null; then
    echo "✅ Redis iniciado correctamente."
else
    echo "❌ No se pudo iniciar Redis."
fi
