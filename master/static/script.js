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
 */
function pollForResult() {
	fetch("/status")
		.then(response => response.json())
		.then(data => {
			if (data.done && data.redirect) {
				// Redirecciona al usuario cuando el procesamiento esté completo
				window.location.href = data.redirect;
			} else {
				// Espera 2 segundos y vuelve a consultar
				setTimeout(pollForResult, 2000);
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

	if (imageInput.files.length === 0) return;

	const file = imageInput.files[0];
	const reader = new FileReader();

	// Callback cuando se ha leído completamente el archivo como base64
	reader.onload = async function () {
		const imageBase64 = reader.result;

		const formData = new FormData();
		formData.append("image", imageBase64);
		formData.append("filter", filterSelect.value);

		// Cambia la pantalla a modo progreso
		showScreen("progress");

		try {
			// Envia imagen y filtro al backend
			const response = await fetch("/process", {
				method: "POST",
				body: formData,
			});

			const data = await response.json();
			if (data.status === "ok") {
				// Si todo va bien, comienza a hacer polling para ver si ya terminó
				pollForResult();
			}
		} catch (error) {
			console.error("Error al enviar imagen:", error);
			alert("Hubo un error al procesar la imagen.");
		}
	};

	// Inicia la lectura del archivo como base64
	reader.readAsDataURL(file);
});
