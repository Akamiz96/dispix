# utils/image_reconstructor.py

import numpy as np
import cv2
import os
from base64 import b64decode

def reconstruir_y_guardar_imagen(received_data, output_path, num_rows=4, num_cols=4):
    """
    Reconstruye una imagen a partir de bloques base64 y la guarda como PNG.

    :param received_data: Diccionario con bloques codificados en base64. Llaves tipo 'i_j'.
    :param output_path: Ruta donde guardar la imagen final.
    :param num_rows: Número de filas de bloques.
    :param num_cols: Número de columnas de bloques.
    """
    h_total, w_total = None, None
    bloques = {}

    for block_id, b64data in received_data.items():
        i, j = map(int, block_id.split("_"))
        img_bytes = b64decode(b64data)
        block_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        if block_img is not None:
            bloques[(i, j)] = block_img
            if h_total is None or w_total is None:
                bh, bw = block_img.shape[:2]
                h_total, w_total = bh * num_rows, bw * num_cols

    full_image = np.zeros((h_total, w_total, 3), dtype=np.uint8)

    for (i, j), block in bloques.items():
        bh, bw = block.shape[:2]
        full_image[i*bh:(i+1)*bh, j*bw:(j+1)*bw] = block

    cv2.imwrite(output_path, full_image)
    print(f"🖼️ Imagen reconstruida guardada en {output_path}")
