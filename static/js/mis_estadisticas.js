"use strict";

(() => {
    const panel = document.getElementById("estadisticas-alumno");

    if (!panel) {
        return;
    }

    const apiUrl = panel.dataset.apiUrl;
    const estado = document.getElementById("estado");
    const contenido = document.getElementById("contenido");
    const reintentar = document.getElementById("reintentar");
    const ranking = document.getElementById("ranking");
    const sinReservas = document.getElementById("sin-reservas");

    const campos = [
        "talleres_vigentes",
        "clases_contratadas_vigentes",
        "reservas_proximas",
        "total_reservas",
        "reservas_canceladas"
    ];

    async function cargarEstadisticas() {
        contenido.hidden = true;
        reintentar.hidden = true;
        reintentar.disabled = true;

        estado.textContent = "Cargando tus estadísticas…";

        try {
            const respuesta = await fetch(apiUrl, {
                credentials: "same-origin",
                cache: "no-store"
            });

            const tipoContenido =
                respuesta.headers.get("content-type") || "";

            if (!tipoContenido.includes("application/json")) {
                throw new Error(
                    "La respuesta no es válida. Comprueba que tu sesión siga abierta."
                );
            }

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error?.mensaje ||
                    "No se pudieron cargar las estadísticas."
                );
            }

            if (
                !datos.estadisticas ||
                !Array.isArray(datos.mis_talleres_mas_reservados) ||
                campos.some(
                    campo => !Number.isFinite(datos.estadisticas[campo])
                )
            ) {
                throw new Error(
                    "La API devolvió datos incompletos. Intenta nuevamente."
                );
            }

            // Mostrar los valores personales recibidos desde la API.
            for (const campo of campos) {
                document.getElementById(campo).textContent =
                    datos.estadisticas[campo];
            }

            // Crear la lista sin interpretar los nombres como HTML.
            ranking.replaceChildren();

            for (const taller of datos.mis_talleres_mas_reservados) {
                const fila = document.createElement("li");
                const etiqueta =
                    taller.reservas === 1 ? "reserva" : "reservas";

                fila.textContent =
                    `${taller.taller}: ${taller.reservas} ${etiqueta}`;

                ranking.appendChild(fila);
            }

            sinReservas.hidden =
                datos.mis_talleres_mas_reservados.length !== 0;

            estado.textContent = "";
            contenido.hidden = false;

        } catch (error) {
            estado.textContent = error instanceof TypeError
                ? "No se pudo conectar con el servidor. Intenta nuevamente."
                : error.message || "No se pudieron cargar tus estadísticas.";

            reintentar.hidden = false;

        } finally {
            reintentar.disabled = false;
        }
    }

    reintentar.addEventListener("click", cargarEstadisticas);

    cargarEstadisticas();
})();