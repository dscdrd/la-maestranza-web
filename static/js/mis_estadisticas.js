"use strict";

(() => {

    /* ======================================================
        ELEMENTOS
       ====================================================== */

    const pagina =
        document.getElementById(
            "estadisticas-alumno"
        );


    if (!pagina) {
        return;
    }


    const apiUrl =
        pagina.dataset.apiUrl;


    const estado =
        document.getElementById(
            "estado"
        );


    const contenido =
        document.getElementById(
            "contenido"
        );


    const botonReintentar =
        document.getElementById(
            "reintentar"
        );


    const descripcionAlumno =
        document.getElementById(
            "descripcion-alumno"
        );


    const talleresVigentes =
        document.getElementById(
            "talleres_vigentes"
        );


    const clasesContratadas =
        document.getElementById(
            "clases_contratadas"
        );


    const reservasProximas =
        document.getElementById(
            "reservas_proximas"
        );


    const reservasCanceladas =
        document.getElementById(
            "reservas_canceladas"
        );


    const rankingTalleres =
        document.getElementById(
            "ranking-talleres"
        );


    const sinTalleres =
        document.getElementById(
            "sin-talleres"
        );


    const resumenReservas =
        document.getElementById(
            "resumen-reservas"
        );



    /* ======================================================
        RENDERIZAR TALLERES
       ====================================================== */

    function mostrarTalleres(talleres) {

        rankingTalleres.innerHTML = "";


        if (
            !Array.isArray(talleres) ||
            talleres.length === 0
        ) {

            sinTalleres.hidden =
                false;

            return;

        }


        sinTalleres.hidden =
            true;


        talleres.forEach(
            (taller) => {

                const fila =
                    document.createElement(
                        "article"
                    );


                fila.className =
                    "estadistica-taller";


                const cantidad =
                    Number(
                        taller.reservas || 0
                    );


                const palabraReserva =
                    cantidad === 1
                        ? "reserva"
                        : "reservas";


                fila.innerHTML = `
                    <div class="nombre-taller">

                        <h3>
                            ${taller.taller}
                        </h3>

                        <span>
                            Actividad registrada
                        </span>

                    </div>


                    <div class="numero-reservas">

                        <strong>
                            ${cantidad}
                        </strong>

                        <span>
                            ${palabraReserva}
                        </span>

                    </div>
                `;


                rankingTalleres.appendChild(
                    fila
                );

            }
        );

    }



    /* ======================================================
        CARGAR ESTADÍSTICAS
       ====================================================== */

    async function cargarEstadisticas() {

        estado.hidden =
            false;


        estado.textContent =
            "Cargando estadísticas…";


        contenido.hidden =
            true;


        botonReintentar.hidden =
            true;


        try {

            const respuesta =
                await fetch(
                    apiUrl,
                    {
                        method: "GET",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        credentials:
                            "same-origin",

                        cache:
                            "no-store"
                    }
                );


            const datos =
                await respuesta.json();


            if (!respuesta.ok) {

                const mensajeError =
                    datos.error?.mensaje ||
                    "No se pudieron cargar las estadísticas.";


                throw new Error(
                    mensajeError
                );

            }


            /* ==============================================
                ALUMNO
               ============================================== */

            if (datos.alumno) {

                descripcionAlumno.textContent =
                    `${datos.alumno.nombre} ${datos.alumno.apellido}, esta es una vista general de tu actividad en La Maestranza.`;

            }



            /* ==============================================
                    ESTADÍSTICAS
               ============================================== */

            const estadisticas =
                datos.estadisticas || {};


            talleresVigentes.textContent =
                estadisticas
                    .talleres_vigentes ?? 0;


            clasesContratadas.textContent =
                estadisticas
                    .clases_contratadas_vigentes ?? 0;


            reservasProximas.textContent =
                estadisticas
                    .reservas_proximas ?? 0;


            reservasCanceladas.textContent =
                estadisticas
                    .reservas_canceladas ?? 0;



            /* ==============================================
                RESUMEN HISTÓRICO
               ============================================== */

            const totalReservas =
                estadisticas
                    .total_reservas ?? 0;


            resumenReservas.textContent =
                `${totalReservas} reservas registradas en tu historial.`;



            /*  ==============================================
                TALLERES
               ============================================== */

            mostrarTalleres(
                datos
                    .mis_talleres_mas_reservados ||
                []
            );



            /* ==============================================
                    MOSTRAR CONTENIDO
               ============================================== */

            estado.hidden =
                true;


            contenido.hidden =
                false;


        } catch (error) {

            contenido.hidden =
                true;


            estado.hidden =
                false;


            estado.textContent =
                error.message ||
                "No se pudieron cargar las estadísticas.";


            botonReintentar.hidden =
                false;

        }

    }



    /* ======================================================
        REINTENTAR
       ====================================================== */

    botonReintentar.addEventListener(
        "click",
        cargarEstadisticas
    );



    /* ======================================================
        INICIO
       ====================================================== */

    cargarEstadisticas();

})();