# ------------------------------------------------------------------------------
# ARCHIVO: utils/logger.py
# DESCRIPCIÓN: Utilidad para registrar tiempos de procesamiento de tareas
#              distribuidas en DisPix. Guarda la información en un archivo CSV.
#
# AUTOR: Alejandro Castro Martínez
# FECHA: 17 de abril de 2025
# DEPENDENCIAS: built-in (csv, os, datetime)
# ------------------------------------------------------------------------------

import csv
import os
import time

# Ruta del archivo de log
LOG_CSV_PATH = "data/logs/processing_times.csv"

def registrar_tiempo_procesamiento(task_id, image_size, block_size, num_blocks, filtro, start_time):
    """
    Registra en un archivo CSV el tiempo total de procesamiento de una tarea.

    Parámetros:
        task_id (str): ID de la transacción.
        image_size (tuple): Tamaño de la imagen original (ancho, alto).
        block_size (tuple): Tamaño de cada bloque (ancho, alto).
        num_blocks (int): Número total de bloques enviados.
        filtro (str): Filtro aplicado a la imagen.
        start_time (datetime): Momento en que comenzó el procesamiento.

    Retorna:
        None
    """
    print(f"Saving processing time for task {task_id}...")
    end_time = time.time()
    processing_time = (end_time - start_time)

    file_exists = os.path.isfile(LOG_CSV_PATH)

    # Crear carpeta si no existe
    os.makedirs(os.path.dirname(LOG_CSV_PATH), exist_ok=True)

    with open(LOG_CSV_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "task_id", "image_size", "block_size",
                "num_blocks", "filter", "processing_time_sec"
            ])
        writer.writerow([
            task_id,
            f"{image_size[0]}x{image_size[1]}",
            f"{block_size[0]}x{block_size[1]}",
            num_blocks,
            filtro,
            f"{processing_time:.3f}"
        ])
