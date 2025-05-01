# ------------------------------------------------------------------------------
# ARCHIVO: app.py
# DESCRIPCIÓN: Servidor principal del sistema DisPix. Implementado con Flask,
#              gestiona la interfaz web, la carga de imágenes, la división en
#              bloques, la publicación de tareas en Redis y la reconstrucción de
#              la imagen al recibir los resultados.
# AUTOR: Alejandro Castro Martínez
# FECHA DE CREACIÓN: 2025-04-17
# ÚLTIMA MODIFICACIÓN: 2025-04-17
# DEPENDENCIAS: flask, numpy, opencv-python, redis, base64, werkzeug, logging
# CONTEXTO:
#     - Proyecto DisPix: procesamiento distribuido de imágenes.
#     - Este archivo constituye el "máster" del sistema.
# ------------------------------------------------------------------------------

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
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
from utils.logger import registrar_tiempo_procesamiento
from utils.recovery import iniciar_verificacion_recuperacion

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

# Diccionario para llevar el estado de todas las tareas activas (clave: task_id)
task_store = {}

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
    block_size = int(request.form["block_size"])

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

    # Dividir en bloques 
    h, w, _ = image.shape
    num_rows, num_cols = block_size, block_size
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

    # Guardar el estado de la tarea actual en el diccionario task_store
    task_store[task_id] = {
        "start_time": time.time(),
        "blocks_sent": len(blocks),
        "total_blocks": len(blocks),
        "blocks_received": 0,
        "received_data": {},
        "width": w,
        "height": h,
        "block_width": num_rows,
        "block_height": num_cols,
        "filter": filtro,
        "task_id": task_id,
        "image_blocks": blocks,
        "retries": 0,
        "max_retries": 1
    }

    # Publicar cada bloque como tarea en Redis
    for block in blocks:
        publish_block(block["task_id"], block["block_id"], block["filter"], block["data"])
        app.logger.info(f"🟢 Publicando bloque {block['block_id']} con filtro {block['filter']}")

    # Iniciar verificación de recuperación automática por reintento
    iniciar_verificacion_recuperacion(task_store[task_id])

    return jsonify({"status": "ok", "blocks": len(blocks), "task_id": task_id})

# Recepción de bloques procesados por parte de los workers
@app.route("/result", methods=["POST"])
def receive_result():
    data = request.json
    task_id = data["task_id"]
    block_id = data["block_id"]
    block_data = data["block_data"]

    task = task_store.get(task_id)
    if not task:
        return jsonify({"status": "error", "message": "Tarea no encontrada"}), 404

    # Guardar bloque recibido
    task["blocks_received"] += 1
    task["received_data"][block_id] = block_data

    total = task["total_blocks"]
    received = task["blocks_received"]

    # Logging de recepción
    ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.logger.info(f"{timestamp} - IP: {ip} - Acceso a /result - Bloque: {block_id} - Recibido: {received}/{total}")

    # Verificar si ya llegaron todos los bloques
    if received == total:
        total_time = time.time() - task["start_time"]
        print(f"✅ Procesamiento completo en {total_time:.2f} segundos.")

        filename = f"reconstructed_{task_id}.png"
        output_path = os.path.join(PROCESSED_IMAGES, filename)
        reconstruir_y_guardar_imagen(task["received_data"], output_path,
                                     num_rows=task["block_width"], num_cols=task["block_height"])

        task["original_filename"] = f"uploaded_{task_id}.png"
        task["processed_filename"] = filename

        registrar_tiempo_procesamiento(
            task_id=task_id,
            image_size=(task["width"], task["height"]),
            block_size=(task["block_width"], task["block_height"]),
            num_blocks=task["blocks_sent"],
            filtro=task["filter"],
            start_time=task["start_time"]
        )

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
    task = task_store.get(task_id)
    if not task:
        return "Tarea no encontrada", 404

    original = task.get("original_filename")
    processed = task.get("processed_filename")
    return render_template("results.html", task_id=task_id, original_filename=original, processed_filename=processed)

# Endpoint para hacer polling y verificar si la tarea ya terminó
@app.route("/status")
def check_status():
    task_id = request.args.get("task_id")
    task = task_store.get(task_id)
    if not task:
        return jsonify({"done": False, "error": True, "message": "Tarea no encontrada"}), 404

    is_done = task["blocks_received"] == task["total_blocks"]
    has_error = task.get("error", False)
    has_retry = task.get("retries", 0) > 0

    return jsonify({
        "done": is_done or has_error,
        "redirect": url_for("result_page", task_id=task_id) if is_done and not has_error else None,
        "retry": has_retry,
        "error": has_error
    })

@app.route('/download/<filename>')
def download_image(filename):
    return send_from_directory(
        directory='data/processed_images',
        path=filename,
        as_attachment=True
    )

# Ejecutar servidor local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
