# 🧩 Carpeta `workers/` – Workers de procesamiento en DisPix

Esta carpeta contiene los **nodos trabajadores** del sistema DisPix. Los workers son responsables de:
1. Escuchar tareas desde un canal Redis.
2. Procesar bloques de imagen aplicando filtros.
3. Enviar los resultados procesados de vuelta al máster vía HTTP POST.

---

## ⚙️ Contenido

```
workers/
├── requirements.txt        # Dependencias necesarias para ejecutar el worker
├── subscriber_redis.py     # Worker principal: se suscribe, procesa y responde

└── utils/
    └── image_filters.py    # Implementación de filtros: negativo, desenfoque, pixelado
```

---

## 🔁 Flujo del Worker

1. Se conecta al canal Redis (`dispix-tasks`).
2. Espera nuevos mensajes con tareas.
3. Al recibir una tarea:
   - Decodifica el bloque de imagen (base64).
   - Aplica el filtro solicitado.
   - Envía los resultados mediante POST al endpoint `/result` del máster.

---

## ▶️ Ejecución

Desde el directorio raíz del proyecto:
```bash
cd workers
python subscriber_redis.py
```

Puedes lanzar varios workers simultáneamente para observar procesamiento paralelo.

---

## 📦 Requisitos

Instala las dependencias con:
```bash
pip install -r requirements.txt
```

---

## 🧠 Notas adicionales

- Los filtros se definen en `utils/image_filters.py`.
- El canal Redis usado debe coincidir con el del máster (`dispix-tasks`).
- Se recomienda ejecutar Redis antes de iniciar los workers.

---
