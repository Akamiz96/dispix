/*
------------------------------------------------------------------------------
ARCHIVO: script.js
DESCRIPCIÓN: Controla la lógica del frontend para la carga de imágenes,
             selección de filtros y visualización de pantallas en la interfaz
             web del sistema DisPix. También gestiona la espera del resultado
             procesado mediante polling al backend.
AUTOR: Alejandro Castro Martínez
FECHA DE CREACIÓN: 2025-04-17
ÚLTIMA MODIFICACIÓN: 2025-04-17
DEPENDENCIAS: HTML DOM, fetch API
CONTEXTO:
    - Proyecto DisPix.
    - Este script es cargado en la plantilla index.html para habilitar
      la funcionalidad de subida y procesamiento de imágenes.
------------------------------------------------------------------------------
*/

/**
 * Muestra una pantalla específica ocultando las demás.
 * Se utiliza para alternar entre la carga, el progreso y los resultados.
 * 
 * @param {string} screenId - El sufijo del id de la pantalla a mostrar (ej: 'progress').
 */
function showScreen(screenId) {
	const screens = document.querySelectorAll(".screen");
	screens.forEach((screen) => screen.classList.remove("active"));
	document.getElementById("screen-" + screenId).classList.add("active");
}

/**
 * Función de polling que consulta al servidor cada 2 segundos
 * para verificar si el resultado ya está disponible.
 * Si lo está, redirige automáticamente a la página de resultados.
 * 
 * @param {string} taskId - Identificador único de la tarea que se está procesando.
 */
function pollForResult(taskId) {
	fetch("/status?task_id=" + taskId)
		.then(response => response.json())
		.then(data => {
			if (data.retry) {
				const retryMsg = document.getElementById("retry-message");
				if (retryMsg) retryMsg.style.display = "block";
			}

			if (data.done) {
				if (data.error) {
					showScreen("error");
				} else if (data.redirect) {
					window.location.href = data.redirect;
				}
			} else {
				setTimeout(() => pollForResult(taskId), 2000);
			}
		});
}

/**
 * Manejador del evento de envío del formulario de carga.
 * Lee la imagen seleccionada, la codifica en base64 y la envía
 * junto con el filtro seleccionado al backend usando fetch.
 */
document.getElementById("upload-form").addEventListener("submit", async function (e) {
	e.preventDefault();

	const imageInput = document.getElementById("image-input");
	const filterSelect = document.getElementById("filter-select");
	const blockSizeInput = document.getElementById("block-size-input");

	// Validación del archivo
	if (imageInput.files.length === 0) return;

	// Validación del tamaño del bloque
	const blockSize = parseInt(blockSizeInput.value);
	if (isNaN(blockSize) || blockSize < 1 || blockSize > 1024) {
		alert("⚠️ El tamaño del bloque debe estar entre 1 y 1024 píxeles.");
		return;
	}

	const file = imageInput.files[0];
	const reader = new FileReader();

	// Callback cuando se ha leído completamente el archivo como base64
	reader.onload = async function () {
		const imageBase64 = reader.result;

		const formData = new FormData();
		formData.append("image", imageBase64);
		formData.append("filter", filterSelect.value);
		formData.append("block_size", blockSize);  // 🧩 nuevo dato enviado

		// Cambia la pantalla a modo progreso
		showScreen("progress");

		try {
			// Envia imagen, filtro y tamaño de bloque al backend
			const response = await fetch("/process", {
				method: "POST",
				body: formData,
			});

			const data = await response.json();
			if (data.status === "ok") {
				// 🆕 Extraer taskId del backend para hacer seguimiento independiente
				const taskId = data.task_id;

				// Si todo va bien, comienza a hacer polling para ver si ya terminó
				pollForResult(taskId);
			}
		} catch (error) {
			console.error("Error al enviar imagen:", error);
			alert("Hubo un error al procesar la imagen.");
		}
	};

	// Inicia la lectura del archivo como base64
	reader.readAsDataURL(file);
});
