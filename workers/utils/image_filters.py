"""
------------------------------------------------------------------------------
ARCHIVO: image_filters.py
DESCRIPCIÓN: Contiene la lógica de filtros de imagen utilizados por los workers
             en el sistema DisPix. Cada filtro toma un bloque de imagen en
             formato OpenCV y retorna el bloque procesado según el filtro
             especificado.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: OpenCV (cv2), numpy
CONTEXTO:
    - Proyecto DisPix: procesamiento distribuido de imágenes.
    - Este archivo es importado por subscriber_redis.py para aplicar el filtro
      indicado en cada tarea.
------------------------------------------------------------------------------
"""

import cv2
import numpy as np

def aplicar_filtro(img, filtro):
    """
    Aplica un filtro de imagen sobre un bloque dado.

    Args:
        img (np.ndarray): Imagen original en formato OpenCV.
        filtro (str): Tipo de filtro a aplicar ('negative', 'blur', 'pixelate').

    Returns:
        np.ndarray: Imagen procesada con el filtro solicitado.
    """

    if filtro == "negative":
        # Invierte los valores de los píxeles para crear un efecto negativo
        return cv2.bitwise_not(img)

    elif filtro == "blur":
        # Aplica desenfoque gaussiano con un kernel 15x15
        return cv2.GaussianBlur(img, (15, 15), 0)

    elif filtro == "pixelate":
        # Reduce la imagen y la vuelve a escalar para crear efecto pixelado
        h, w = img.shape[:2]
        temp = cv2.resize(img, (w // 10, h // 10), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)

    else:
        # Si el filtro no se reconoce, se devuelve la imagen sin modificar
        return img
