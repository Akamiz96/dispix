# 🔗 Carpeta `pub-sub/` – Comunicación Redis en DisPix

Esta carpeta contiene los **scripts de soporte para Redis** en el sistema DisPix. Incluye utilidades para iniciar/detener Redis localmente, así como pruebas de envío y recepción de mensajes a través del canal pub/sub utilizado por el máster y los workers.

---

## ⚙️ Contenido

```
pub-sub/
├── requirements.txt        # Dependencias para los scripts de prueba

├── data/
│   └── logs/               # Logs de ejecución de pruebas de comunicación

├── scripts/
│   ├── start_redis.sh      # Script para iniciar el servidor Redis localmente
│   └── stop_redis.sh       # Script para detener Redis de forma controlada

└── test-redis/             # Pruebas de pub/sub
    ├── publisher_test.py       # Publicador de prueba
    ├── subscriber_test.py      # Suscriptor de prueba
    └── run_test.sh             # Ejecuta ambos en conjunto para validar la conexión
```

---

## 📡 Propósito de esta carpeta

- Probar el canal de comunicación Redis (`dispix-tasks`) de forma aislada.
- Garantizar que los workers y el máster pueden publicar y suscribirse correctamente.
- Automatizar el despliegue local de Redis para pruebas simples.

---

## ▶️ Ejecución de pruebas

Desde la raíz del proyecto:
```bash
cd pub-sub/test-redis
bash run_test.sh
```

Este script ejecutará un publisher y un subscriber, mostrando los mensajes intercambiados por Redis.

---

## 🚀 Redis local

Puedes iniciar y detener Redis usando:
```bash
# Iniciar
bash pub-sub/scripts/start_redis.sh

# Detener
bash pub-sub/scripts/stop_redis.sh
```

Asegúrate de tener Redis instalado localmente y disponible en tu `$PATH` para que estos scripts funcionen correctamente.

---

## 🏗️ Instalación de Redis

### 🔧 En Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
```
Puedes verificar que Redis esté corriendo con:
```bash
redis-cli ping
# Debería responder: PONG
```

### 🪟 En Windows
1. Descarga el instalador desde:
   [https://github.com/tporadowski/redis/releases](https://github.com/tporadowski/redis/releases)

2. Elige el archivo `.msi` o `.zip`, instala y agrega la ruta del ejecutable a tu variable de entorno `PATH`.

3. Verifica su funcionamiento en CMD o PowerShell:
```bash
redis-server
```
Y en otra terminal:
```bash
redis-cli ping
```

---

## 📦 Requisitos

Instala las dependencias necesarias con:
```bash
pip install -r requirements.txt
```

---