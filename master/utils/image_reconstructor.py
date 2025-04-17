"""
------------------------------------------------------------------------------
ARCHIVO: image_reconstructor.py
DESCRIPCIÓN: Este módulo se encarga de reconstruir una imagen completa a partir
             de bloques individuales codificados en base64, los cuales han sido
             procesados por los workers del sistema DisPix. La imagen final se
             guarda como archivo PNG.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: numpy, opencv-python (cv2), base64, os
CONTEXTO:
    - Proyecto DisPix: sistema distribuido de procesamiento de imágenes.
    - Se utiliza desde el máster al recibir todos los bloques procesados.
------------------------------------------------------------------------------
"""

import numpy as np
import cv2
import os
from base64 import b64decode

def reconstruir_y_guardar_imagen(received_data, output_path, num_rows=4, num_cols=4):
    """
    Reconstruye una imagen a partir de bloques codificados en base64 y la guarda como PNG.

    Args:
        received_data (dict): Diccionario con los bloques recibidos, cuyas llaves son strings
                              del tipo 'i_j' indicando su posición, y los valores son strings
                              base64 representando imágenes en formato PNG o JPG.
        output_path (str): Ruta donde se guardará la imagen final.
        num_rows (int): Número de filas esperadas de bloques.
        num_cols (int): Número de columnas esperadas de bloques.
    """

    h_total, w_total = None, None  # Altura y ancho total de la imagen final
    bloques = {}  # Almacena los bloques ya decodificados por posición (i, j)

    # Decodificación y lectura de cada bloque
    for block_id, b64data in received_data.items():
        i, j = map(int, block_id.split("_"))  # Extrae posición i, j
        img_bytes = b64decode(b64data)        # Decodifica base64 a bytes
        block_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

        if block_img is not None:
            bloques[(i, j)] = block_img

            # Determinar tamaño final si es la primera vez
            if h_total is None or w_total is None:
                bh, bw = block_img.shape[:2]
                h_total, w_total = bh * num_rows, bw * num_cols

    # Crear imagen vacía del tamaño final
    full_image = np.zeros((h_total, w_total, 3), dtype=np.uint8)

    # Ubicar cada bloque en su posición correspondiente
    for (i, j), block in bloques.items():
        bh, bw = block.shape[:2]
        full_image[i*bh:(i+1)*bh, j*bw:(j+1)*bw] = block

    # Guardar imagen resultante en disco
    cv2.imwrite(output_path, full_image)
    print(f"🖼️ Imagen reconstruida guardada en {output_path}")
