"use strict";

(() => {

    const pagina = document.getElementById("crear-taller");

    if (!pagina) {
        return;
    }


    const formulario =
        document.getElementById("form-crear-taller");

    const mensaje =
        document.getElementById("mensaje-formulario");

    const apiUrl =
        pagina.dataset.apiUrl;

    const gestionUrl =
        pagina.dataset.gestionUrl;


    // ======================================================
    // ENVIAR FORMULARIO
    // ======================================================

    formulario.addEventListener("submit", async (evento) => {

        evento.preventDefault();


        const boton =
            formulario.querySelector(".btn-guardar");

        boton.disabled = true;
        boton.textContent = "Creando...";

        mensaje.hidden = true;
        mensaje.className = "mensaje-formulario";


        // ==================================================
        // PREPARAR DATOS
        // ==================================================

        const datos = {

            nombre:
                formulario.nombre.value.trim(),

            descripcion:
                formulario.descripcion.value.trim(),

            horario:
                formulario.horario.value.trim(),

            cupo_maximo:
                Number(formulario.cupo_maximo.value),

            imagen:
                formulario.imagen.value.trim()
        };


        try {

            // ==============================================
            // POST A LA API
            // ==============================================

            const respuesta = await fetch(apiUrl, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                credentials: "same-origin",

                body: JSON.stringify(datos)

            });


            const resultado =
                await respuesta.json();


            if (!respuesta.ok) {

                throw new Error(
                    resultado.error ||
                    "No se pudo crear el taller."
                );
            }


            // ==============================================
            // ÉXITO
            // ==============================================

            mensaje.textContent =
                "Taller creado correctamente.";

            mensaje.classList.add("exito");
            mensaje.hidden = false;


            formulario.reset();


            // ==============================================
            // VOLVER A GESTIÓN
            // ==============================================

            setTimeout(() => {

                window.location.href = gestionUrl;

            }, 1000);


        } catch (error) {

            // ==============================================
            // ERROR
            // ==============================================

            mensaje.textContent =
                error.message ||
                "Ocurrió un error al crear el taller.";

            mensaje.classList.add("error");
            mensaje.hidden = false;


        } finally {

            boton.disabled = false;
            boton.textContent = "Crear taller";

        }

    });

})();