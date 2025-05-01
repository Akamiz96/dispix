# ------------------------------------------------------------------------------
# ARCHIVO: utils/recovery.py
# DESCRIPCIÓN: Lógica de recuperación para bloques faltantes en DisPix. Verifica
#                si todos los bloques han sido recibidos y reintenta publicar
#                aquellos que no llegaron, hasta un máximo de reintentos.
# AUTOR: Alejandro Castro Martínez
# FECHA: 2025-04-17
# DEPENDENCIAS: threading, time
# ------------------------------------------------------------------------------

import threading
import time
from utils.redis_publisher import publish_block

def iniciar_verificacion_recuperacion(task_ref):
    threading.Thread(target=verificar_bloques_completos, args=(task_ref,), daemon=True).start()

def verificar_bloques_completos(task_ref):
    timeout_total = 30  # segundos
    intervalo = 10       # cada cuanto revisar
    intentos = timeout_total // intervalo

    for _ in range(intentos):
        if task_ref["blocks_received"] >= task_ref["blocks_sent"]:
            return  # todo recibido
        time.sleep(intervalo)

    # revisar si faltaron bloques
    missing = [
        i for i in range(task_ref["blocks_sent"])
        if str(i) not in task_ref["received_data"]
    ]

    if missing and task_ref.get("retries", 0) < task_ref.get("max_retries", 2):
        task_ref["retries"] = task_ref.get("retries", 0) + 1
        print(f"⚠️ Reintentando bloques faltantes: {missing}")

        for i in missing:
            bloque = task_ref["image_blocks"][i]
            publish_block(bloque["task_id"], bloque["block_id"], bloque["filter"], bloque["data"])

        verificar_bloques_completos(task_ref)  # vuelve a intentar
    elif missing:
        print(f"❌ Faltaron bloques incluso tras reintentos: {missing}")
        task_ref["error"] = True
