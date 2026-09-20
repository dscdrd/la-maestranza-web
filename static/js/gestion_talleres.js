"use strict";

(() => {

    const pagina =
        document.getElementById("gestion-talleres");

    if (!pagina) {
        return;
    }

    const apiBase =
        pagina.dataset.apiBase;


    // ======================================================
    // BOTONES ELIMINAR
    // ======================================================

    const botones =
        document.querySelectorAll(".btn-eliminar");


    botones.forEach((boton) => {

        boton.addEventListener(
            "click",
            async () => {

                const idTaller =
                    boton.dataset.idTaller;

                const nombreTaller =
                    boton.dataset.nombreTaller;


                // ==========================================
                // CONFIRMACIÓN
                // ==========================================

                const confirmar = window.confirm(
                    `¿Seguro que deseas eliminar "${nombreTaller}"?\n\n` +
                    "Esta acción eliminará el taller de forma permanente."
                );


                if (!confirmar) {
                    return;
                }


                boton.disabled = true;
                boton.textContent = "Eliminando...";


                try {

                    // ======================================
                    // DELETE API REST
                    // ======================================

                    const respuesta =
                        await fetch(
                            `${apiBase}/${idTaller}`,
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
                            "No se pudo eliminar el taller."
                        );
                    }


                    // ======================================
                    // ÉXITO
                    // ======================================

                    alert(
                        "Taller eliminado correctamente."
                    );


                    window.location.reload();


                } catch (error) {

                    alert(
                        error.message ||
                        "Ocurrió un error al eliminar el taller."
                    );

                    boton.disabled = false;
                    boton.textContent = "Eliminar";

                }

            }
        );

    });

})();