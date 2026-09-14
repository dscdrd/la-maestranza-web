"use strict";

(() => {

    const panel = document.getElementById("estadisticas-profesor");

    if (!panel) {
        return;
    }

    const apiUrl = panel.dataset.apiUrl;

    const estado = document.getElementById("estado");
    const contenido = document.getElementById("contenido");
    const reintentar = document.getElementById("reintentar");

    const rankingTalleres =
        document.getElementById("ranking-talleres");

    const sinTalleres =
        document.getElementById("sin-talleres");


    const campos = [
        "talleres_asignados",
        "alumnos_activos",
        "proximas_clases",
        "reservas_activas",
        "reservas_canceladas",
        "ocupacion_promedio"
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
                !Array.isArray(datos.talleres) ||
                campos.some(
                    campo =>
                        !Number.isFinite(
                            Number(datos.estadisticas[campo])
                        )
                )
            ) {

                throw new Error(
                    "La API devolvió datos incompletos. Intenta nuevamente."
                );
            }


            // =========================================
            // MOSTRAR MÉTRICAS
            // =========================================

            for (const campo of campos) {

                const elemento =
                    document.getElementById(campo);

                let valor =
                    datos.estadisticas[campo];


                if (campo === "ocupacion_promedio") {

                    valor =
                        `${Number(valor).toFixed(2)} %`;
                }


                elemento.textContent = valor;
            }


            // =========================================
            // MOSTRAR ESTADÍSTICAS POR TALLER
            // =========================================

            rankingTalleres.replaceChildren();


            for (const taller of datos.talleres) {

                const tarjeta =
                    document.createElement("article");

                tarjeta.classList.add(
                    "tarjeta",
                    "tarjeta-taller-estadistica"
                );


                const titulo =
                    document.createElement("h3");

                titulo.textContent =
                    taller.taller;


                const detalle =
                    document.createElement("div");

                detalle.classList.add(
                    "detalle-estadisticas-taller"
                );


                const datosTaller = [

                    {
                        etiqueta: "Clases creadas",
                        valor: Number(
                            taller.total_clases || 0
                        )
                    },

                    {
                        etiqueta: "Cupos totales",
                        valor: Number(
                            taller.cupos_totales || 0
                        )
                    },

                    {
                        etiqueta: "Reservas activas",
                        valor: Number(
                            taller.reservas_activas || 0
                        )
                    },

                    {
                        etiqueta: "Reservas canceladas",
                        valor: Number(
                            taller.reservas_canceladas || 0
                        )
                    },

                    {
                        etiqueta: "Ocupación",
                        valor:
                            `${Number(
                                taller.porcentaje_ocupacion || 0
                            ).toFixed(2)} %`
                    }

                ];


                for (const dato of datosTaller) {

                    const fila =
                        document.createElement("div");

                    fila.classList.add(
                        "fila-estadistica-taller"
                    );


                    const etiqueta =
                        document.createElement("span");

                    etiqueta.textContent =
                        dato.etiqueta;


                    const valor =
                        document.createElement("strong");

                    valor.textContent =
                        dato.valor;


                    fila.appendChild(etiqueta);
                    fila.appendChild(valor);

                    detalle.appendChild(fila);
                }


                tarjeta.appendChild(titulo);
                tarjeta.appendChild(detalle);

                rankingTalleres.appendChild(
                    tarjeta
                );
            }


            // =========================================
            // MENSAJE SI NO HAY TALLERES
            // =========================================

            sinTalleres.hidden =
                datos.talleres.length !== 0;


            estado.textContent = "";

            contenido.hidden = false;


        } catch (error) {

            estado.textContent =
                error instanceof TypeError
                    ? "No se pudo conectar con el servidor. Intenta nuevamente."
                    : error.message ||
                      "No se pudieron cargar tus estadísticas.";

            reintentar.hidden = false;


        } finally {

            reintentar.disabled = false;
        }
    }


    reintentar.addEventListener(
        "click",
        cargarEstadisticas
    );


    cargarEstadisticas();

})();