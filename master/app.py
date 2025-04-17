"""
------------------------------------------------------------------------------
ARCHIVO: app.py
DESCRIPCIÓN: Servidor principal del sistema DisPix. Implementado con Flask,
             gestiona la interfaz web, la carga de imágenes, la división en
             bloques, la publicación de tareas en Redis y la reconstrucción de
             la imagen al recibir los resultados.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: flask, numpy, opencv-python, redis, base64, werkzeug, logging
CONTEXTO:
    - Proyecto DisPix: procesamiento distribuido de imágenes.
    - Este archivo constituye el "máster" del sistema.
------------------------------------------------------------------------------
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, redirect
import os
import time
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from base64 import b64decode
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import uuid

from utils.redis_publisher import publish_block
from utils.image_reconstructor import reconstruir_y_guardar_imagen

# Configuración de Flask
app = Flask(__name__)

# Rutas de carpetas usadas
UPLOAD_FOLDER = "data/uploaded_images"
RECEIVED_DIR = "data/received_blocks"
PROCESSED_IMAGES = "data/processed_images"
LOG_DIR = "data/logs"

# Crear carpetas si no existen
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_DIR, exist_ok=True)
os.makedirs(PROCESSED_IMAGES, exist_ok=True)

# Diccionario para llevar el estado de la tarea actual
current_task = {
    "start_time": None,
    "blocks_sent": 0,
    "blocks_received": 0,
    "total_blocks": 0,
    "received_data": {}
}

# Configuración de logs rotativos por día
log_filename = os.path.join(LOG_DIR, "log_" + datetime.now().strftime("%Y-%m-%d") + ".log")

handler = TimedRotatingFileHandler(
    filename=log_filename,
    when="midnight",
    interval=1,
    backupCount=7,  # guarda los últimos 7 días
    encoding='utf-8',
    delay=False,
)
handler.suffix = "%Y-%m-%d"
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Ruta principal: muestra el formulario de carga
@app.route("/")
def index():
    if request.method == "GET":
        ip = request.remote_addr
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app.logger.info(f"{timestamp} - IP: {ip} - Acceso a /")
    return render_template("index.html")

# Procesamiento de la imagen: guarda, divide y publica
@app.route("/process", methods=["POST"])
def process_image():
    task_id = str(uuid.uuid4())
    image_data = request.form["image"]
    filtro = request.form["filter"]

    # Decodificar base64
    header, encoded = image_data.split(",", 1)
    img_bytes = b64decode(encoded)

    # Guardar la imagen original
    filename = secure_filename(f"uploaded_{task_id}.png")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    # Leer imagen con OpenCV
    image = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

    # Dividir en bloques (4x4 por defecto)
    h, w, _ = image.shape
    num_rows, num_cols = 4, 4
    bh, bw = h // num_rows, w // num_cols
    blocks = []

    for i in range(num_rows):
        for j in range(num_cols):
            block = image[i*bh:(i+1)*bh, j*bw:(j+1)*bw]
            block_id = f"{i}_{j}"
            blocks.append({
                "task_id": task_id,
                "block_id": block_id,
                "data": block,
                "filter": filtro
            })

    # Inicializar estado de la tarea
    current_task.update({
        "start_time": time.time(),
        "blocks_sent": len(blocks),
        "total_blocks": len(blocks),
        "blocks_received": 0,
        "received_data": {},
        "task_id": task_id
    })

    # Publicar cada bloque como tarea en Redis
    for block in blocks:
        publish_block(block["task_id"], block["block_id"], block["filter"], block["data"])
        app.logger.info(f"🟢 Publicando bloque {block['block_id']} con filtro {block['filter']}")

    return jsonify({"status": "ok", "blocks": len(blocks)})

# Recepción de bloques procesados por parte de los workers
@app.route("/result", methods=["POST"])
def receive_result():
    data = request.json
    task_id = data["task_id"]
    block_id = data["block_id"]
    block_data = data["block_data"]

    # Guardar bloque recibido
    current_task["blocks_received"] += 1
    current_task["received_data"][block_id] = block_data

    total = current_task["total_blocks"]
    received = current_task["blocks_received"]

    # Logging de recepción
    ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.logger.info(f"{timestamp} - IP: {ip} - Acceso a /result - Bloque: {block_id} - Recibido: {received}/{total}")

    # Verificar si ya llegaron todos los bloques
    if received == total:
        total_time = time.time() - current_task["start_time"]
        print(f"✅ Procesamiento completo en {total_time:.2f} segundos.")

        filename = f"reconstructed_{task_id}.png"
        output_path = os.path.join(PROCESSED_IMAGES, filename)
        reconstruir_y_guardar_imagen(current_task["received_data"], output_path)

        current_task["original_filename"] = f"uploaded_{task_id}.png"
        current_task["processed_filename"] = filename

        return jsonify({
            "status": "ok",
            "blocks": received,
            "redirect": url_for("result_page", task_id=task_id)
        })

    return jsonify({"status": "ok"})

# Ruta para servir imágenes originales
@app.route("/uploaded_images/<filename>")
def uploaded_images(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Ruta para servir imágenes procesadas
@app.route("/processed_images/<filename>")
def processed_images(filename):
    return send_from_directory(PROCESSED_IMAGES, filename)

# Página final de resultados
@app.route("/result/<task_id>")
def result_page(task_id):
    print(f"Accediendo a la página de resultados para la tarea {task_id}")
    original = current_task.get("original_filename")
    processed = current_task.get("processed_filename")
    return render_template("results.html", original_filename=original, processed_filename=processed)

# Endpoint para hacer polling y verificar si la tarea ya terminó
@app.route("/status")
def check_status():
    is_done = current_task["blocks_received"] == current_task["total_blocks"]
    task_id = current_task.get("task_id")
    if is_done:
        return jsonify({
            "done": True,
            "redirect": url_for("result_page", task_id=task_id)
        })
    else:
        return jsonify({"done": False})

# Ejecutar servidor local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
