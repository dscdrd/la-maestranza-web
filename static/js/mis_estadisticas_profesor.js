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
    // CARGAR ESTADÍSTICAS DESDE LA API
    // ========================================================

    async function cargarEstadisticas() {

        contenido.hidden = true;
        reintentar.hidden = true;

        estado.textContent = "Cargando estadísticas…";

        try {

            const respuesta = await fetch(apiUrl, {
                credentials: "same-origin",
                cache: "no-store"
            });

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error ||
                    "No se pudieron cargar las estadísticas."
                );
            }


            // =================================================
            // ESTADÍSTICAS GENERALES
            // =================================================

            document.getElementById(
                "talleres_asignados"
            ).textContent = datos.talleres_asignados;

            document.getElementById(
                "alumnos_activos"
            ).textContent = datos.alumnos_activos;

            document.getElementById(
                "reservas_activas"
            ).textContent = datos.reservas_activas;

            document.getElementById(
                "reservas_canceladas"
            ).textContent = datos.reservas_canceladas;


            // =================================================
            // ESTADÍSTICAS POR TALLER
            // =================================================

            contenedorTalleres.replaceChildren();

            for (const taller of datos.talleres) {

                const tarjeta =
                    document.createElement("article");

                tarjeta.classList.add("estadistica-taller");


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

                titulo.textContent = taller.nombre;


                const resumen =
                    document.createElement("span");

                resumen.textContent =
                    `${taller.alumnos_activos} alumnos · ` +
                    `${taller.reservas_activas} reservas`;


                encabezado.appendChild(titulo);
                encabezado.appendChild(resumen);


                // ---------------------------------------------
                // OCUPACIÓN
                // ---------------------------------------------

                const ocupacion = crearBarra(
                    "Ocupación",
                    taller.ocupacion
                );


                // ---------------------------------------------
                // ASISTENCIA
                // ---------------------------------------------

                const asistencia = crearBarra(
                    "Asistencia",
                    taller.asistencia
                );


                // ---------------------------------------------
                // DETALLE DE ASISTENCIA
                // ---------------------------------------------

                const detalle =
                    document.createElement("p");

                detalle.classList.add(
                    "detalle-asistencia"
                );

                detalle.textContent =
                    `${taller.presentes} presentes · ` +
                    `${taller.ausentes} ausentes · ` +
                    `${taller.reservas_canceladas} canceladas`;


                tarjeta.appendChild(encabezado);
                tarjeta.appendChild(ocupacion);
                tarjeta.appendChild(asistencia);
                tarjeta.appendChild(detalle);

                contenedorTalleres.appendChild(tarjeta);
            }


            // =================================================
            // SIN TALLERES
            // =================================================

            sinTalleres.hidden =
                datos.talleres.length !== 0;


            estado.textContent = "";
            contenido.hidden = false;


        } catch (error) {

            estado.textContent =
                error.message ||
                "No se pudieron cargar las estadísticas.";

            reintentar.hidden = false;

        }
    }


    // ========================================================
    // CREAR BARRA DE PORCENTAJE
    // ========================================================

    function crearBarra(etiqueta, porcentaje) {

        const valor =
            Math.min(
                100,
                Math.max(0, Number(porcentaje) || 0)
            );


        const bloque =
            document.createElement("div");

        bloque.classList.add("bloque-barra");


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

        fondo.classList.add("barra-fondo");


        const progreso =
            document.createElement("div");

        progreso.classList.add("barra-progreso");

        progreso.style.width = `${valor}%`;


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