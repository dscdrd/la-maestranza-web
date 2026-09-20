"use strict";

(() => {

    const formulario =
        document.getElementById("form-editar-clase");

    if (!formulario) {
        return;
    }

    const apiUrl =
        formulario.dataset.apiUrl;

    const volverUrl =
        formulario.dataset.volverUrl;

    const mensaje =
        document.getElementById("mensaje-formulario");

    const boton =
        formulario.querySelector(".btn-guardar");


    formulario.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();

            boton.disabled = true;
            boton.textContent = "Guardando...";

            const datos = {

                fecha:
                    formulario.fecha.value,

                hora_inicio:
                    formulario.hora_inicio.value,

                hora_fin:
                    formulario.hora_fin.value,

                cupo_maximo:
                    Number(formulario.cupo_maximo.value)

            };


            try {

                const respuesta = await fetch(
                    apiUrl,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        credentials: "same-origin",

                        body: JSON.stringify(datos)
                    }
                );


                const resultado =
                    await respuesta.json();


                if (!respuesta.ok) {

                    throw new Error(
                        resultado.error ||
                        "No se pudo actualizar la clase."
                    );

                }


                mensaje.textContent =
                    "Clase actualizada correctamente.";


                setTimeout(() => {

                    window.location.href =
                        volverUrl;

                }, 700);


            } catch (error) {

                mensaje.textContent =
                    error.message ||
                    "Ocurrió un error al actualizar la clase.";


            } finally {

                boton.disabled = false;

                boton.textContent =
                    "Guardar cambios";

            }

        }
    );

})();