from flask import Flask, render_template, request, jsonify
import os
import time
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from base64 import b64decode
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import os

from utils.redis_publisher import publish_block
from utils.image_reconstructor import reconstruir_y_guardar_imagen
import uuid 

app = Flask(__name__)
UPLOAD_FOLDER = "data/uploads"
RECEIVED_DIR = "data/received_blocks"
PROCESSED_IMAGES = "data/processed_images"
LOG_DIR = "data/logs"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECEIVED_DIR, exist_ok=True)
os.makedirs(PROCESSED_IMAGES, exist_ok=True)

# Estado global
current_task = {
    "start_time": None,
    "blocks_sent": 0,
    "blocks_received": 0,
    "total_blocks": 0,
    "received_data": {}
}

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


@app.route("/")
def index():
    if request.method == "GET":
        ip = request.remote_addr
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app.logger.info(f"{timestamp} - IP: {ip} - Acceso a /")
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process_image():
    task_id = str(uuid.uuid4())

    image_data = request.form["image"]
    filtro = request.form["filter"]

    # Limpiar base64
    header, encoded = image_data.split(",", 1)
    img_bytes = b64decode(encoded)

    # Guardar imagen original
    filename = secure_filename(f"uploaded_{task_id}.png")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    # Cargar con OpenCV
    image = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

    # Dividir en bloques
    h, w, _ = image.shape
    num_rows, num_cols = 4, 4  # Cambiar según el número de bloques deseado
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

    current_task["start_time"] = time.time()
    current_task["blocks_sent"] = len(blocks)
    current_task["total_blocks"] = len(blocks)
    current_task["blocks_received"] = 0
    current_task["received_data"] = {}
    current_task["task_id"] = task_id

    for block in blocks:
        task_id = block["task_id"]
        block_id = block["block_id"]
        filter = block["filter"]
        block_data = block["data"]

        # Publicar bloque en Redis
        publish_block(task_id, block_id, filter, block_data)
        app.logger.info(f"🟢 Publicando bloque {block_id} con filtro {filter}")

    return jsonify({"status": "ok", "blocks": len(blocks)})

@app.route("/result", methods=["POST"])
def receive_result():
    data = request.json
    task_id = data["task_id"]
    block_id = data["block_id"]
    filter = data["filter"]
    block_data = data["block_data"]  # base64

    # Guardar el bloque
    current_task["blocks_received"] += 1
    current_task["received_data"][block_id] = block_data

    total = current_task["total_blocks"]
    received = current_task["blocks_received"]

    ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.logger.info(f"{timestamp} - IP: {ip} - Acceso a /result - Bloque: {block_id} - Recibido: {received}/{total}")

    if current_task["blocks_received"] == current_task["total_blocks"]:
        total_time = time.time() - current_task["start_time"]
        print(f"✅ Procesamiento completo en {total_time:.2f} segundos.")
        
        task_id = current_task.get("task_id", "unknown")
        output_path = os.path.join(PROCESSED_IMAGES, f"reconstructed_{task_id}.png")
        reconstruir_y_guardar_imagen(current_task["received_data"], output_path)


    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)