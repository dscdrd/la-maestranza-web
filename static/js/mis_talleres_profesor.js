"use strict";

(() => {

    const formularios =
        document.querySelectorAll(".form-clase");


    if (!formularios.length) {
        return;
    }


    formularios.forEach((formulario) => {

        formulario.addEventListener(
            "submit",
            async (evento) => {

                evento.preventDefault();


                const idTaller =
                    formulario.dataset.idTaller;

                const boton =
                    formulario.querySelector(".btn-crear");


                boton.disabled = true;
                boton.textContent = "Creando...";


                // ==========================================
                // PREPARAR DATOS
                // ==========================================

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

                    // ======================================
                    // POST API REST
                    // ======================================

                    const respuesta =
                        await fetch(
                            `/api/talleres/${idTaller}/clases`,
                            {
                                method: "POST",

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
                            "No se pudo crear la clase."
                        );

                    }


                    // ======================================
                    // ÉXITO
                    // ======================================

                    alert(
                        "Clase creada correctamente."
                    );


                    window.location.reload();


                } catch (error) {

                    alert(
                        error.message ||
                        "Ocurrió un error al crear la clase."
                    );


                } finally {

                    boton.disabled = false;
                    boton.textContent = "Crear clase";

                }

            }
        );

    });

// ==========================================================
// CANCELAR CLASE
// ==========================================================

const botonesCancelar =
    document.querySelectorAll(".btn-cancelar-clase");


botonesCancelar.forEach((boton) => {

    boton.addEventListener(
        "click",
        async () => {

            const idClase =
                boton.dataset.idClase;


            const confirmar = window.confirm(
                "¿Estás seguro de que deseas cancelar esta clase?"
            );


            if (!confirmar) {
                return;
            }


            boton.disabled = true;
            boton.textContent = "Cancelando...";


            try {

                const respuesta = await fetch(
                    `/api/clases/${idClase}/cancelar`,
                    {
                        method: "PUT",
                        credentials: "same-origin"
                    }
                );


                const resultado =
                    await respuesta.json();


                if (!respuesta.ok) {

                    throw new Error(
                        resultado.error ||
                        "No se pudo cancelar la clase."
                    );

                }


                alert(
                    "Clase cancelada correctamente."
                );


                window.location.reload();


            } catch (error) {

                alert(
                    error.message ||
                    "Ocurrió un error al cancelar la clase."
                );


                boton.disabled = false;
                boton.textContent = "Cancelar";

            }

        }
    );

});


// ==========================================================
// ELIMINAR CLASE FÍSICAMENTE
// ==========================================================

const botonesEliminar =
    document.querySelectorAll(".btn-eliminar-clase");


botonesEliminar.forEach((boton) => {

    boton.addEventListener(
        "click",
        async () => {

            const idClase =
                boton.dataset.idClase;


            const confirmar = window.confirm(
                "¿Estás seguro de que deseas eliminar permanentemente esta clase?"
            );


            if (!confirmar) {
                return;
            }


            boton.disabled = true;
            boton.textContent = "Eliminando...";


            try {

                const respuesta = await fetch(
                    `/api/clases/${idClase}`,
                    {
                        method: "DELETE",
                        credentials: "same-origin"
                    }
                );


                const resultado =
                    await respuesta.json();


                if (!respuesta.ok) {

                    throw new Error(
                        resultado.error ||
                        "No se pudo eliminar la clase."
                    );

                }


                alert(
                    "Clase eliminada permanentemente."
                );


                window.location.reload();


            } catch (error) {

                alert(
                    error.message ||
                    "Ocurrió un error al eliminar la clase."
                );


                boton.disabled = false;
                boton.textContent = "Eliminar";

            }

        }
    );

});

})();