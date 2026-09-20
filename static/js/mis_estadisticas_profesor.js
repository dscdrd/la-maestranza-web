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

    const contenedorTalleres =
        document.getElementById("ranking-talleres");

    const sinTalleres =
        document.getElementById("sin-talleres");


    // ========================================================
    // CARGAR ESTADÍSTICAS
    // ========================================================

    async function cargarEstadisticas() {

        contenido.hidden = true;
        reintentar.hidden = true;

        estado.textContent = "Cargando estadísticas…";


        try {

            const respuesta = await fetch(
                apiUrl,
                {
                    credentials: "same-origin",
                    cache: "no-store"
                }
            );


            const datos = await respuesta.json();


            if (!respuesta.ok) {

                let mensaje = "No se pudieron cargar las estadísticas.";

                if (
                    datos.error
                    && typeof datos.error === "object"
                    && datos.error.mensaje
                ) {
                    mensaje = datos.error.mensaje;
                }

                else if (typeof datos.error === "string") {
                    mensaje = datos.error;
                }


                throw new Error(mensaje);
            }


            // ==================================================
            // ESTADÍSTICAS GENERALES
            // ==================================================

            const estadisticas = datos.estadisticas || {};


            document.getElementById(
                "talleres_asignados"
            ).textContent =
                estadisticas.talleres_asignados ?? 0;


            document.getElementById(
                "alumnos_activos"
            ).textContent =
                estadisticas.alumnos_activos ?? 0;


            document.getElementById(
                "reservas_activas"
            ).textContent =
                estadisticas.reservas_activas ?? 0;


            document.getElementById(
                "reservas_canceladas"
            ).textContent =
                estadisticas.reservas_canceladas ?? 0;


            // ==================================================
            // ESTADÍSTICAS POR TALLER
            // ==================================================

            contenedorTalleres.replaceChildren();


            const talleres = datos.talleres || [];


            for (const taller of talleres) {

                const tarjeta =
                    document.createElement("article");

                tarjeta.classList.add(
                    "estadistica-taller"
                );


                // ---------------------------------------------
                // ENCABEZADO
                // ---------------------------------------------

                const encabezado =
                    document.createElement("div");

                encabezado.classList.add(
                    "encabezado-taller"
                );


                const titulo =
                    document.createElement("h3");

                titulo.textContent =
                    taller.taller ?? "Taller";


                const resumen =
                    document.createElement("span");

                resumen.textContent =
                    `${taller.total_clases ?? 0} clases · ` +
                    `${taller.reservas_activas ?? 0} reservas`;


                encabezado.appendChild(titulo);
                encabezado.appendChild(resumen);


                // ---------------------------------------------
                // OCUPACIÓN
                // ---------------------------------------------

                const ocupacion = crearBarra(
                    "Ocupación",
                    taller.porcentaje_ocupacion ?? 0
                );


                // ---------------------------------------------
                // RESERVAS CANCELADAS
                // ---------------------------------------------

                const detalle =
                    document.createElement("p");

                detalle.classList.add(
                    "detalle-asistencia"
                );

                detalle.textContent =
                    `${taller.reservas_activas ?? 0} activas · ` +
                    `${taller.reservas_canceladas ?? 0} canceladas · ` +
                    `${taller.cupos_totales ?? 0} cupos acumulados`;


                tarjeta.appendChild(encabezado);
                tarjeta.appendChild(ocupacion);
                tarjeta.appendChild(detalle);

                contenedorTalleres.appendChild(tarjeta);
            }


            // ==================================================
            // SIN TALLERES
            // ==================================================

            sinTalleres.hidden =
                talleres.length !== 0;


            estado.textContent = "";
            contenido.hidden = false;


        } catch (error) {

            console.error(
                "Error al cargar estadísticas:",
                error
            );

            estado.textContent =
                error.message
                || "No se pudieron cargar las estadísticas.";

            reintentar.hidden = false;
        }
    }


    // ========================================================
    // CREAR BARRA DE PORCENTAJE
    // ========================================================

    function crearBarra(
        etiqueta,
        porcentaje
    ) {

        const valor = Math.min(
            100,
            Math.max(
                0,
                Number(porcentaje) || 0
            )
        );


        const bloque =
            document.createElement("div");

        bloque.classList.add(
            "bloque-barra"
        );


        const informacion =
            document.createElement("div");

        informacion.classList.add(
            "informacion-barra"
        );


        const nombre =
            document.createElement("span");

        nombre.textContent = etiqueta;


        const numero =
            document.createElement("strong");

        numero.textContent =
            `${valor.toFixed(1)} %`;


        informacion.appendChild(nombre);
        informacion.appendChild(numero);


        const fondo =
            document.createElement("div");

        fondo.classList.add(
            "barra-fondo"
        );


        const progreso =
            document.createElement("div");

        progreso.classList.add(
            "barra-progreso"
        );

        progreso.style.width =
            `${valor}%`;


        fondo.appendChild(progreso);

        bloque.appendChild(informacion);
        bloque.appendChild(fondo);


        return bloque;
    }


    // ========================================================
    // REINTENTAR
    // ========================================================

    reintentar.addEventListener(
        "click",
        cargarEstadisticas
    );


    // ========================================================
    // INICIAR
    // ========================================================

    cargarEstadisticas();

})();