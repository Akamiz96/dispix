function showScreen(screenId) {
	const screens = document.querySelectorAll(".screen");
	screens.forEach((screen) => screen.classList.remove("active"));
	document.getElementById("screen-" + screenId).classList.add("active");
}

function pollForResult() {
	fetch("/status")
		.then(response => response.json())
		.then(data => {
			if (data.done && data.redirect) {
				window.location.href = data.redirect;
			} else {
				setTimeout(pollForResult, 2000); // revisa de nuevo en 2 segundos
			}
		});
}

document.getElementById("upload-form").addEventListener("submit", async function (e) {
	e.preventDefault();

	const imageInput = document.getElementById("image-input");
	const filterSelect = document.getElementById("filter-select");

	if (imageInput.files.length === 0) return;

	const file = imageInput.files[0];
	const reader = new FileReader();

	reader.onload = async function () {
		const imageBase64 = reader.result;

		const formData = new FormData();
		formData.append("image", imageBase64);
		formData.append("filter", filterSelect.value);

		showScreen("progress");

		try {
			const response = await fetch("/process", {
				method: "POST",
				body: formData,
			});

			const data = await response.json();
			if (data.status === "ok") {
				pollForResult();  // inicia el chequeo cada 2 segundos
			}
		} catch (error) {
			console.error("Error al enviar imagen:", error);
			alert("Hubo un error al procesar la imagen.");
		}
	};

	reader.readAsDataURL(file);
});
