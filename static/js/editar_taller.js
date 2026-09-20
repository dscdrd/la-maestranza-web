"use strict";

(() => {

    const pagina =
        document.getElementById("editar-taller");

    if (!pagina) {
        return;
    }


    const formulario =
        document.getElementById("form-editar-taller");

    const boton =
        document.getElementById("btn-guardar");

    const mensaje =
        document.getElementById("mensaje-formulario");


    const apiUrl =
        pagina.dataset.apiUrl;

    const gestionUrl =
        pagina.dataset.gestionUrl;


    // ======================================================
    // EDITAR TALLER
    // ======================================================

    formulario.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();


            boton.disabled = true;
            boton.textContent = "Guardando...";

            mensaje.hidden = true;


            // ==================================================
            // PREPARAR JSON
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
                // PUT A LA API REST
                // ==============================================

                const respuesta =
                    await fetch(apiUrl, {

                        method: "PUT",

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
                        "No se pudo actualizar el taller."
                    );
                }


                // ==============================================
                // ÉXITO
                // ==============================================

                mensaje.textContent =
                    "Taller actualizado correctamente.";

                mensaje.hidden = false;


                setTimeout(() => {

                    window.location.href =
                        gestionUrl;

                }, 1000);


            } catch (error) {

                // ==============================================
                // ERROR
                // ==============================================

                mensaje.textContent =
                    error.message ||
                    "Ocurrió un error al actualizar el taller.";

                mensaje.hidden = false;


            } finally {

                boton.disabled = false;
                boton.textContent = "Guardar cambios";

            }

        }
    );

})();