const selector = document.getElementById("taller");
const mensaje = document.getElementById("mensaje");

const detalle = document.getElementById("detalle-taller");
const nombreTaller = document.getElementById("nombre-taller");
const descripcionTaller = document.getElementById("descripcion-taller");
const horarioTaller = document.getElementById("horario-taller");
const cupoTaller = document.getElementById("cupo-taller");

let talleres = [];

async function cargarTalleres() {
    try {
        const respuesta = await fetch(selector.dataset.apiUrl);

        if (!respuesta.ok) {
            throw new Error("Falló la consulta de talleres.");
        }

        const datos = await respuesta.json();

        if (!Array.isArray(datos.talleres)) {
            throw new Error("La respuesta no contiene una lista de talleres.");
        }

        talleres = datos.talleres;

        selector.replaceChildren(
            new Option("Elige un taller", "")
        );

        if (talleres.length === 0) {
            selector.replaceChildren(
                new Option("Sin talleres disponibles", "")
            );

            mensaje.textContent = "Todavía no hay talleres registrados.";
            return;
        }

        for (const taller of talleres) {
            selector.add(
                new Option(taller.nombre, taller.id_taller)
            );
        }

        selector.disabled = false;
        mensaje.textContent = "Elige uno de nuestros talleres.";

    } catch (error) {
        selector.disabled = true;

        selector.replaceChildren(
            new Option("No se pudieron cargar los talleres", "")
        );

        detalle.hidden = true;

        mensaje.textContent =
            "No pudimos cargar la lista. Recarga la página para intentarlo nuevamente.";

        console.error(error);
    }
}

selector.addEventListener("change", () => {
    const taller = talleres.find(
        (taller) => String(taller.id_taller) === selector.value
    );

    if (!taller) {
        detalle.hidden = true;
        mensaje.textContent = "Elige uno de nuestros talleres.";
        return;
    }

    nombreTaller.textContent = taller.nombre;

    descripcionTaller.textContent =
        taller.descripcion || "Descripción pendiente.";

    horarioTaller.textContent =
        taller.horario || "Horario por confirmar.";

    cupoTaller.textContent = taller.cupo_maximo == null
        ? "Por confirmar"
        : `${taller.cupo_maximo} personas`;

    detalle.hidden = false;
    mensaje.textContent = `Seleccionaste: ${taller.nombre}`;
});

cargarTalleres();