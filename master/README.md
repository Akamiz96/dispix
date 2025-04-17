# 📂 Carpeta `master/` – Servidor principal DisPix

Esta carpeta contiene el núcleo del sistema DisPix. Aquí se encuentra la lógica del **servidor Flask**, el cual actúa como máster en la arquitectura distribuida. Se encarga de recibir imágenes, dividirlas en bloques, publicar tareas a Redis, recolectar los resultados procesados y reconstruir la imagen final.

---

## ⚙️ Contenido

```
master/
├── app.py                  # Servidor Flask: entrada principal del sistema
├── requirements.txt        # Dependencias necesarias para ejecutar el máster

├── data/                   # Carpetas de almacenamiento interno
│   ├── logs/               # Información de depuración y mensajes del servidor
│   ├── processed_images/   # Imágenes finales después del procesamiento
│   ├── received_blocks/    # Bloques individuales recibidos desde los workers
│   └── uploaded_images/    # Imágenes originales subidas por los usuarios

├── static/                 # Recursos estáticos para la interfaz web
│   ├── favicon.ico
│   ├── logo.png
│   ├── script.js           # Lógica del cliente para redirecciones, AJAX, etc.
│   └── style.css           # Estilo visual de la interfaz

├── templates/              # Plantillas HTML renderizadas con Flask
│   ├── index.html          # Página principal con el formulario de carga
│   └── results.html        # Página de resultados después del procesamiento

└── utils/                  # Funciones auxiliares del máster
    ├── image_reconstructor.py  # Une bloques procesados en una imagen completa
    └── redis_publisher.py      # Publica tareas al canal Redis (dispix-tasks)
```

---

## 🚀 Funcionalidades principales

- Interfaz web para subir imágenes y elegir filtros.
- División automática en bloques.
- Envío de tareas a Redis.
- Recepción de resultados desde los workers por POST.
- Reconstrucción y almacenamiento de la imagen final.

---

## ▶️ Ejecución

Desde el directorio raíz del proyecto:
```bash
cd master
python app.py
```

El servidor se ejecutará en `http://localhost:5000`

---

## 📦 Requisitos

Instala las dependencias con:
```bash
pip install -r requirements.txt
```

---

## 🧠 Notas adicionales

- Esta carpeta **no contiene lógica de procesamiento de imagen**, solo gestión y coordinación.
- El servidor espera resultados en el endpoint `/result`.
- La reconstrucción se basa en el orden de los `block_id` recibidos.

---