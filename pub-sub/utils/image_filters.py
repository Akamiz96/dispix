# utils/image_filters.py

import cv2
import numpy as np

def aplicar_filtro(img, filtro):
    if filtro == "negative":
        return cv2.bitwise_not(img)
    elif filtro == "blur":
        return cv2.GaussianBlur(img, (15, 15), 0)
    elif filtro == "pixelate":
        h, w = img.shape[:2]
        temp = cv2.resize(img, (w // 10, h // 10), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
    else:
        # Si no se reconoce el filtro, se retorna la imagen tal cual
        return img
