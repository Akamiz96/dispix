let totalBlocks = 16; // Simulación
let sentBlocks = 0;
let receivedBlocks = 0;
let startTime = null;

// Navegación entre pantallas
function showScreen(id) {
	document
		.querySelectorAll(".screen")
		.forEach((div) => div.classList.remove("active"));
	document.getElementById(id).classList.add("active");
}

function updateProgressBars() {
	const sentPercent = Math.round((sentBlocks / totalBlocks) * 100);
	const receivedPercent = Math.round((receivedBlocks / totalBlocks) * 100);

	document.getElementById("progress-sent").style.width = `${sentPercent}%`;
	document.getElementById("progress-sent").textContent = `${sentPercent}%`;

	document.getElementById(
		"progress-received"
	).style.width = `${receivedPercent}%`;
	document.getElementById(
		"progress-received"
	).textContent = `${receivedPercent}%`;
}

// Procesar formulario
document.getElementById("upload-form").addEventListener("submit", function (e) {
	e.preventDefault();

	const fileInput = document.getElementById("image-input");
	const filter = document.getElementById("filter-select").value;

	if (!fileInput.files.length) {
		alert("Selecciona una imagen.");
		return;
	}

	const file = fileInput.files[0];
	const reader = new FileReader();

	reader.onload = function (event) {
		const imgData = event.target.result;

		// Mostrar imagen original en resultado
		document.getElementById("original-image").src = imgData;

		// Aquí iniciaríamos procesamiento real
		simulateProcessing(imgData, filter);
	};

	reader.readAsDataURL(file);
});

function simulateProcessing(imageData, filter) {
	startTime = Date.now();
	showScreen("screen-progress");
	sentBlocks = 0;
	receivedBlocks = 0;
	updateProgressBars();

	// Enviar imagen y filtro al servidor
	fetch("/process", {
		method: "POST",
		body: new URLSearchParams({
			image: imageData,
			filter: filter,
		}),
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
		},
	})
		.then((res) => res.json())
		.then((data) => {
			totalBlocks = data.blocks || 16;
			simulatePubSub(totalBlocks); // solo para simular progreso por ahora
		});
}

function simulatePubSub(count) {
	let sendInterval = setInterval(() => {
		if (sentBlocks < count) {
			sentBlocks++;
			updateProgressBars();
		} else {
			clearInterval(sendInterval);

			let receiveInterval = setInterval(() => {
				if (receivedBlocks < count) {
					receivedBlocks++;
					updateProgressBars();
				} else {
					clearInterval(receiveInterval);
					showFinalResult();
				}
			}, 300);
		}
	}, 100);
}

function showFinalResult() {
	const endTime = Date.now();
	const seconds = ((endTime - startTime) / 1000).toFixed(2);
	// document.getElementById("processing-time").textContent = seconds;

	// Simular imagen procesada (por ahora, usar la misma)
	document.getElementById("processed-image").src =
		document.getElementById("original-image").src;

	showScreen("screen-result");
}

function goToUpload() {
	document.getElementById("upload-form").reset();
	showScreen("screen-upload");
}
