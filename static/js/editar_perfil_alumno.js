"use strict";

(() => {

    /* ======================================================
       FORMULARIO DE PERFIL
       ====================================================== */

    const formulario =
        document.getElementById("form-editar-perfil");

    if (!formulario) {
        return;
    }


    const apiPerfilUrl =
        formulario.dataset.apiUrl;

    const panelUrl =
        formulario.dataset.panelUrl;

    const mensajeFormulario =
        document.getElementById("mensaje-formulario");


    /* ======================================================
       ACTUALIZAR DATOS PERSONALES
       ====================================================== */

    formulario.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();

            mensajeFormulario.textContent = "";


            const datos = {

                nombre:
                    formulario.nombre.value.trim(),

                apellido:
                    formulario.apellido.value.trim(),

                telefono:
                    formulario.telefono.value.trim(),

                contacto_emergencia:
                    formulario.contacto_emergencia.value.trim(),

                telefono_emergencia:
                    formulario.telefono_emergencia.value.trim()

            };


            try {

                const respuesta =
                    await fetch(
                        apiPerfilUrl,
                        {
                            method: "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "same-origin",

                            body:
                                JSON.stringify(datos)
                        }
                    );


                const resultado =
                    await respuesta.json();


                if (!respuesta.ok) {

                    throw new Error(
                        resultado.error ||
                        "No se pudo actualizar el perfil."
                    );

                }


                mensajeFormulario.textContent =
                    resultado.mensaje ||
                    "Perfil actualizado correctamente.";


                setTimeout(
                    () => {

                        window.location.href =
                            panelUrl;

                    },
                    900
                );


            } catch (error) {

                mensajeFormulario.textContent =
                    error.message ||
                    "Ocurrió un error al actualizar el perfil.";

            }

        }
    );


    /* ======================================================
       FOTO DE PERFIL
       ====================================================== */

    const btnSeleccionarFoto =
        document.getElementById("btn-seleccionar-foto");

    const inputFoto =
        document.getElementById("foto-perfil");

    const editorFoto =
        document.getElementById("editor-foto");

    const imagenRecorte =
        document.getElementById("imagen-recorte");

    const btnCancelarFoto =
        document.getElementById("btn-cancelar-foto");

    const btnGuardarFoto =
        document.getElementById("btn-guardar-foto");

    const avatarEditar =
        document.getElementById("avatar-editar");


    let cropper = null;


    if (
        btnSeleccionarFoto &&
        inputFoto &&
        editorFoto &&
        imagenRecorte
    ) {

        btnSeleccionarFoto.addEventListener(
            "click",
            () => {

                inputFoto.click();

            }
        );


        inputFoto.addEventListener(
            "change",
            () => {

                const archivo =
                    inputFoto.files[0];


                if (!archivo) {
                    return;
                }


                const tiposPermitidos = [
                    "image/jpeg",
                    "image/png",
                    "image/webp"
                ];


                if (
                    !tiposPermitidos.includes(
                        archivo.type
                    )
                ) {

                    alert(
                        "Selecciona una imagen JPG, PNG o WEBP."
                    );

                    inputFoto.value = "";

                    return;
                }


                const lector =
                    new FileReader();


                lector.onload = (evento) => {

                    imagenRecorte.src =
                        evento.target.result;


                    editorFoto.classList.remove(
                        "oculto"
                    );


                    if (cropper) {

                        cropper.destroy();

                    }


                    cropper =
                        new Cropper(
                            imagenRecorte,
                            {
                                aspectRatio: 1,

                                viewMode: 1,

                                autoCropArea: 1,

                                responsive: true,

                                background: false
                            }
                        );

                };


                lector.readAsDataURL(
                    archivo
                );

            }
        );

    }


    /* ======================================================
       CANCELAR FOTO
       ====================================================== */

    if (btnCancelarFoto) {

        btnCancelarFoto.addEventListener(
            "click",
            () => {

                if (cropper) {

                    cropper.destroy();

                    cropper = null;

                }


                editorFoto.classList.add(
                    "oculto"
                );


                inputFoto.value = "";

            }
        );

    }


    /* ======================================================
       GUARDAR FOTO
       ====================================================== */

    if (btnGuardarFoto) {

        btnGuardarFoto.addEventListener(
            "click",
            () => {

                if (!cropper) {
                    return;
                }


                const canvas =
                    cropper.getCroppedCanvas(
                        {
                            width: 500,
                            height: 500
                        }
                    );


                canvas.toBlob(
                    async (blob) => {

                        if (!blob) {

                            alert(
                                "No se pudo procesar la imagen."
                            );

                            return;
                        }


                        const datosFoto =
                            new FormData();


                        datosFoto.append(
                            "foto",
                            blob,
                            "perfil.jpg"
                        );


                        btnGuardarFoto.disabled =
                            true;


                        btnGuardarFoto.textContent =
                            "Guardando...";


                        try {

                            const respuesta =
                                await fetch(
                                    "/api/alumno/foto",
                                    {
                                        method:
                                            "PUT",

                                        credentials:
                                            "same-origin",

                                        body:
                                            datosFoto
                                    }
                                );


                            const resultado =
                                await respuesta.json();


                            if (!respuesta.ok) {

                                throw new Error(
                                    resultado.error ||
                                    "No se pudo guardar la foto."
                                );

                            }


                            /*
                                Si la API devuelve la URL o nombre
                                de la imagen, actualizamos el avatar.
                            */

                            if (
                                resultado.foto_url
                            ) {

                                avatarEditar.src =
                                    resultado.foto_url;

                            } else {

                                /*
                                    Si tu API no devuelve URL,
                                    recargamos para obtener la
                                    nueva imagen desde Flask.
                                */

                                window.location.reload();

                                return;
                            }


                            editorFoto.classList.add(
                                "oculto"
                            );


                            cropper.destroy();

                            cropper = null;


                            inputFoto.value = "";


                        } catch (error) {

                            alert(
                                error.message ||
                                "Ocurrió un error al guardar la foto."
                            );


                        } finally {

                            btnGuardarFoto.disabled =
                                false;


                            btnGuardarFoto.textContent =
                                "Guardar foto";

                        }

                    },
                    "image/jpeg",
                    0.9
                );

            }
        );

    }


    /* ======================================================
       ELIMINAR CUENTA
       ====================================================== */

    const botonEliminarCuenta =
        document.getElementById(
            "btn-eliminar-cuenta"
        );


    if (botonEliminarCuenta) {

        botonEliminarCuenta.addEventListener(
            "click",
            async () => {

                const confirmar =
                    window.confirm(
                        "¿Estás seguro de que deseas eliminar tu cuenta?\n\n" +
                        "Se eliminarán tus datos, inscripciones, reservas, pagos e historial.\n\n" +
                        "Esta acción no se puede deshacer."
                    );


                if (!confirmar) {
                    return;
                }


                const confirmarDefinitivo =
                    window.confirm(
                        "Última confirmación:\n\n" +
                        "¿Deseas eliminar tu cuenta permanentemente?"
                    );


                if (!confirmarDefinitivo) {
                    return;
                }


                const apiUrl =
                    botonEliminarCuenta.dataset.apiUrl;


                const inicioUrl =
                    botonEliminarCuenta.dataset.inicioUrl;


                botonEliminarCuenta.disabled =
                    true;


                botonEliminarCuenta.textContent =
                    "Eliminando cuenta...";


                try {

                    const respuesta =
                        await fetch(
                            apiUrl,
                            {
                                method:
                                    "DELETE",

                                headers: {
                                    "Accept":
                                        "application/json"
                                },

                                credentials:
                                    "same-origin"
                            }
                        );


                    const resultado =
                        await respuesta.json();


                    if (!respuesta.ok) {

                        throw new Error(
                            resultado.error ||
                            "No se pudo eliminar la cuenta."
                        );

                    }


                    alert(
                        resultado.mensaje ||
                        "Tu cuenta fue eliminada correctamente."
                    );


                    window.location.href =
                        inicioUrl;


                } catch (error) {

                    alert(
                        error.message ||
                        "Ocurrió un error al eliminar la cuenta."
                    );


                    botonEliminarCuenta.disabled =
                        false;


                    botonEliminarCuenta.textContent =
                        "Eliminar mi cuenta";

                }

            }
        );

    }

})();