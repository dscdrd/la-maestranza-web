"use strict";

(() => {

    /* ======================================================
       FORMULARIO
       ====================================================== */

    const formulario =
        document.getElementById(
            "form-registro-alumno"
        );


    if (!formulario) {
        return;
    }


    /* ======================================================
       ELEMENTOS GENERALES
       ====================================================== */

    const apiUrl =
        formulario.dataset.apiUrl;


    const inicioUrl =
        formulario.dataset.inicioUrl;


    const mensaje =
        document.getElementById(
            "mensaje-registro"
        );


    const botonRegistro =
        formulario.querySelector(
            ".btn-registro"
        );


    /* ======================================================
       RUT
       ====================================================== */

    const campoRut =
        document.getElementById("rut");


    /* ======================================================
       REGLAMENTO
       ====================================================== */

    const modalReglamento =
        document.getElementById(
            "modal-reglamento"
        );


    const textoReglamento =
        document.getElementById(
            "texto-reglamento"
        );


    const botonAbrirReglamento =
        document.getElementById(
            "btn-abrir-reglamento"
        );


    const botonCerrarReglamento =
        document.getElementById(
            "btn-cerrar-reglamento"
        );


    const botonReglamentoLeido =
        document.getElementById(
            "btn-reglamento-leido"
        );


    const estadoLectura =
        document.getElementById(
            "estado-lectura"
        );


    const checkCondiciones =
        document.getElementById(
            "acepta_condiciones"
        );


    const avisoReglamento =
        document.getElementById(
            "aviso-reglamento"
        );


    let reglamentoLeido = false;



    /* ======================================================
       FORMATEAR RUT
       ====================================================== */

    campoRut.addEventListener(
        "input",
        () => {

            let rut =
                campoRut.value
                    .toUpperCase();


            /*
                Quitar todo excepto:
                números y K
            */

            rut =
                rut.replace(
                    /[^0-9K]/g,
                    ""
                );


            /*
                Si escribió K, la tratamos
                como dígito verificador.
            */

            if (rut.includes("K")) {

                const numeros =
                    rut
                        .replace(/K/g, "")
                        .slice(0, 8);

                rut =
                    numeros + "K";

            } else {

                rut =
                    rut.slice(0, 9);

            }


            /*
                Agregar guion antes del
                dígito verificador.
            */

            if (rut.length > 1) {

                const cuerpo =
                    rut.slice(0, -1);

                const dv =
                    rut.slice(-1);


                campoRut.value =
                    `${cuerpo}-${dv}`;

            } else {

                campoRut.value = rut;

            }

        }
    );



    /* ======================================================
       VALIDAR RUT CHILENO
       ====================================================== */

    function validarRut(rut) {

        rut =
            rut
                .replace(
                    /[^0-9Kk]/g,
                    ""
                )
                .toUpperCase();


        if (rut.length < 2) {
            return false;
        }


        const cuerpo =
            rut.slice(0, -1);


        const dvIngresado =
            rut.slice(-1);


        if (!/^\d+$/.test(cuerpo)) {
            return false;
        }


        let suma = 0;

        let multiplicador = 2;


        for (
            let i = cuerpo.length - 1;
            i >= 0;
            i--
        ) {

            suma +=
                Number(cuerpo[i]) *
                multiplicador;


            multiplicador++;


            if (multiplicador > 7) {
                multiplicador = 2;
            }

        }


        const resultado =
            11 - (suma % 11);


        let dvCalculado;


        if (resultado === 11) {

            dvCalculado = "0";

        } else if (
            resultado === 10
        ) {

            dvCalculado = "K";

        } else {

            dvCalculado =
                String(resultado);

        }


        return (
            dvIngresado ===
            dvCalculado
        );

    }



    /* ======================================================
       COMPROBAR SI SE LLEGÓ AL FINAL DEL REGLAMENTO
       ====================================================== */

    function comprobarLectura() {

        if (reglamentoLeido) {

            botonReglamentoLeido.disabled =
                false;

            return;

        }


        const posicion =
            textoReglamento.scrollTop +
            textoReglamento.clientHeight;


        const altura =
            textoReglamento.scrollHeight;


        const llegoAlFinal =
            posicion >= altura - 10;


        if (llegoAlFinal) {

            botonReglamentoLeido.disabled =
                false;


            estadoLectura.textContent =
                "Has llegado al final del reglamento.";

        }

    }



    /* ======================================================
       ABRIR REGLAMENTO
       ====================================================== */

    function abrirReglamento() {

        modalReglamento.style.display =
            "flex";


        modalReglamento.setAttribute(
            "aria-hidden",
            "false"
        );


        /*
            Si todavía no ha sido leído,
            comienza desde arriba.
        */

        if (!reglamentoLeido) {

            textoReglamento.scrollTop = 0;


            botonReglamentoLeido.disabled =
                true;


            estadoLectura.textContent =
                "Desplázate hasta el final para continuar.";

        } else {

            botonReglamentoLeido.disabled =
                false;


            estadoLectura.textContent =
                "Reglamento leído.";

        }


        /*
            Si todo el reglamento cabe en
            pantalla sin scroll, igualmente
            permitimos continuar.
        */

        requestAnimationFrame(
            comprobarLectura
        );

    }



    /* ======================================================
       CERRAR REGLAMENTO
       ====================================================== */

    function cerrarReglamento() {

        modalReglamento.style.display =
            "none";


        modalReglamento.setAttribute(
            "aria-hidden",
            "true"
        );

    }



    /* ======================================================
       BOTÓN ABRIR
       ====================================================== */

    botonAbrirReglamento.addEventListener(
        "click",
        abrirReglamento
    );



    /* ======================================================
       BOTÓN CERRAR
       ====================================================== */

    botonCerrarReglamento.addEventListener(
        "click",
        cerrarReglamento
    );



    /* ======================================================
       SCROLL DEL REGLAMENTO
       ====================================================== */

    textoReglamento.addEventListener(
        "scroll",
        comprobarLectura
    );



    /* ======================================================
       CONFIRMAR QUE FUE LEÍDO
       ====================================================== */

    botonReglamentoLeido.addEventListener(
        "click",
        () => {

            if (
                botonReglamentoLeido.disabled
            ) {
                return;
            }


            reglamentoLeido = true;


            /*
                Ahora sí se permite marcar
                el checkbox.
            */

            checkCondiciones.disabled =
                false;


            avisoReglamento.textContent =
                "Reglamento leído. Ahora puedes aceptar las condiciones.";


            estadoLectura.textContent =
                "Reglamento leído.";


            cerrarReglamento();


            /*
                No lo marcamos automáticamente.
                El alumno debe aceptarlo
                voluntariamente.
            */

            checkCondiciones.focus();

        }
    );



    /* ======================================================
       CERRAR HACIENDO CLIC FUERA DE LA VENTANA
       ====================================================== */

    modalReglamento.addEventListener(
        "click",
        (evento) => {

            if (
                evento.target ===
                modalReglamento
            ) {

                cerrarReglamento();

            }

        }
    );



    /* ======================================================
       CERRAR CON ESC
       ====================================================== */

    document.addEventListener(
        "keydown",
        (evento) => {

            if (
                evento.key === "Escape" &&
                modalReglamento.style.display ===
                    "flex"
            ) {

                cerrarReglamento();

            }

        }
    );



    /* ======================================================
       ENVIAR FORMULARIO
       ====================================================== */

    formulario.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();


            mensaje.textContent = "";


            /* ==================================================
               DATOS
               ================================================== */

            const datos = {

                nombre:
                    formulario.nombre
                        .value
                        .trim(),

                apellido:
                    formulario.apellido
                        .value
                        .trim(),

                /*
                    Se quita el guion antes
                    de enviarlo a Python.
                */

                rut:
                    formulario.rut
                        .value
                        .replace(
                            /[^0-9Kk]/g,
                            ""
                        )
                        .toUpperCase(),

                fecha_nacimiento:
                    formulario
                        .fecha_nacimiento
                        .value,

                correo:
                    formulario.correo
                        .value
                        .trim(),

                telefono:
                    formulario.telefono
                        .value
                        .trim(),

                contacto_emergencia:
                    formulario
                        .contacto_emergencia
                        .value
                        .trim(),

                telefono_emergencia:
                    formulario
                        .telefono_emergencia
                        .value
                        .trim(),

                contrasena:
                    formulario
                        .contrasena
                        .value,

                confirmar_contrasena:
                    formulario
                        .confirmar_contrasena
                        .value,

                acepta_condiciones:
                    checkCondiciones.checked

            };



            /* ==================================================
               VALIDAR RUT
               ================================================== */

            /*if (!validarRut(datos.rut)) {

                mensaje.textContent =
                    "El RUT ingresado no es válido.";


                campoRut.focus();


                return;

            }
                */



            /* ==================================================
               VALIDAR CONTRASEÑAS
               ================================================== */

            if (
                datos.contrasena !==
                datos.confirmar_contrasena
            ) {

                mensaje.textContent =
                    "Las contraseñas no coinciden.";


                formulario
                    .confirmar_contrasena
                    .focus();


                return;

            }



            /* ==================================================
               VALIDAR LECTURA REGLAMENTO
               ================================================== */

            if (!reglamentoLeido) {

                mensaje.textContent =
                    "Debes leer el reglamento antes de registrarte.";


                return;

            }



            /* ==================================================
               VALIDAR ACEPTACIÓN
               ================================================== */

            if (
                !datos.acepta_condiciones
            ) {

                mensaje.textContent =
                    "Debes aceptar el reglamento y las condiciones.";


                checkCondiciones.focus();


                return;

            }



            /* ==================================================
               DESACTIVAR BOTÓN
               ================================================== */

            botonRegistro.disabled =
                true;


            botonRegistro.textContent =
                "Registrando...";



            try {

                /* ==============================================
                   POST REST
                   ============================================== */

                const respuesta =
                    await fetch(
                        apiUrl,
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            credentials:
                                "same-origin",

                            body:
                                JSON.stringify(
                                    datos
                                )

                        }
                    );


                const resultado =
                    await respuesta.json();



                if (!respuesta.ok) {

                    throw new Error(
                        resultado.error ||
                        "No se pudo completar el registro."
                    );

                }



                /* ==============================================
                   REGISTRO EXITOSO
                   ============================================== */

                mensaje.textContent =
                    "Cuenta creada correctamente.";


                formulario.reset();


                /*
                    Al resetear el formulario,
                    volvemos a bloquear el
                    reglamento.
                */

                reglamentoLeido =
                    false;


                checkCondiciones.disabled =
                    true;


                avisoReglamento.textContent =
                    "Lee el reglamento completo para habilitar la aceptación.";



                setTimeout(
                    () => {

                        window.location.href =
                            inicioUrl;

                    },
                    1000
                );


            } catch (error) {

                mensaje.textContent =
                    error.message ||
                    "Ocurrió un error al registrar la cuenta.";


            } finally {

                botonRegistro.disabled =
                    false;


                botonRegistro.textContent =
                    "Registrarse";

            }

        }
    );

})();