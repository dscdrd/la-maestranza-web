(() => {

    // ======================================================
    // FORMULARIO
    // ======================================================

    const formulario =
        document.getElementById("form-editar-profesor");

    const mensaje =
        document.getElementById("mensaje-formulario");


    // ======================================================
    // FOTO DE PERFIL
    // ======================================================

    const avatarProfesor =
        document.getElementById("avatar-profesor");

    const botonSeleccionarFoto =
        document.getElementById("btn-seleccionar-foto");

    const inputFoto =
        document.getElementById("foto-perfil");

    const editorFoto =
        document.getElementById("editor-foto");

    const imagenRecorte =
        document.getElementById("imagen-recorte");

    const botonCancelarFoto =
        document.getElementById("btn-cancelar-foto");

    const botonGuardarFoto =
        document.getElementById("btn-guardar-foto");


    let cropper = null;
    let urlTemporal = null;
    let urlPreview = null;

    /*
        Aquí guardaremos temporalmente
        la fotografía recortada.
    */
    let fotoRecortadaBlob = null;


    // ======================================================
    // ABRIR SELECTOR
    // ======================================================

    if (botonSeleccionarFoto && inputFoto) {

        botonSeleccionarFoto.addEventListener(
            "click",
            () => {

                inputFoto.value = "";

                inputFoto.click();

            }
        );

    }


    // ======================================================
    // SELECCIONAR / CAMBIAR FOTO
    // ======================================================

    if (
        inputFoto &&
        imagenRecorte &&
        editorFoto
    ) {

        inputFoto.addEventListener(
            "change",
            () => {

                const archivo =
                    inputFoto.files[0];


                if (!archivo) {
                    return;
                }


                // Validar que sea imagen
                if (
                    !archivo.type.startsWith("image/")
                ) {

                    alert(
                        "Debes seleccionar una imagen válida."
                    );

                    inputFoto.value = "";

                    return;
                }


                // Destruir Cropper anterior
                if (cropper) {

                    cropper.destroy();

                    cropper = null;

                }


                // Liberar URL anterior
                if (urlTemporal) {

                    URL.revokeObjectURL(
                        urlTemporal
                    );

                    urlTemporal = null;

                }


                // Crear URL de la nueva imagen
                urlTemporal =
                    URL.createObjectURL(
                        archivo
                    );


                /*
                    Esperamos a que la imagen cargue
                    antes de crear Cropper.
                */

                imagenRecorte.onload =
                    () => {

                        editorFoto.classList.remove(
                            "oculto"
                        );


                        cropper =
                            new Cropper(
                                imagenRecorte,
                                {
                                    aspectRatio: 1,

                                    viewMode: 1,

                                    dragMode: "move",

                                    autoCropArea: 0.8,

                                    movable: true,

                                    zoomable: true,

                                    scalable: false,

                                    rotatable: false,

                                    responsive: true,

                                    background: false
                                }
                            );

                    };


                imagenRecorte.src =
                    urlTemporal;

            }
        );

    }


    // ======================================================
    // CANCELAR RECORTE
    // ======================================================

    if (botonCancelarFoto) {

        botonCancelarFoto.addEventListener(
            "click",
            () => {

                if (cropper) {

                    cropper.destroy();

                    cropper = null;

                }


                if (urlTemporal) {

                    URL.revokeObjectURL(
                        urlTemporal
                    );

                    urlTemporal = null;

                }


                inputFoto.value = "";

                imagenRecorte.removeAttribute(
                    "src"
                );


                editorFoto.classList.add(
                    "oculto"
                );

            }
        );

    }


    // ======================================================
    // GUARDAR FOTO COMO PREVISUALIZACIÓN
    // ======================================================

    if (botonGuardarFoto) {

        botonGuardarFoto.addEventListener(
            "click",
            () => {

                if (!cropper) {

                    alert(
                        "Primero selecciona una imagen."
                    );

                    return;
                }


                const canvas =
                    cropper.getCroppedCanvas({
                        width: 500,
                        height: 500,

                        imageSmoothingEnabled: true,

                        imageSmoothingQuality:
                            "high"
                    });


                canvas.toBlob(
                    (blob) => {

                        if (!blob) {

                            alert(
                                "No se pudo procesar la imagen."
                            );

                            return;
                        }


                        // Guardar temporalmente
                        fotoRecortadaBlob =
                            blob;


                        // Eliminar preview anterior
                        if (urlPreview) {

                            URL.revokeObjectURL(
                                urlPreview
                            );

                        }


                        // Crear preview
                        urlPreview =
                            URL.createObjectURL(
                                blob
                            );


                        // Cambiar foto visible
                        avatarProfesor.src =
                            urlPreview;


                        // Cerrar Cropper
                        cropper.destroy();

                        cropper = null;


                        editorFoto.classList.add(
                            "oculto"
                        );


                        inputFoto.value = "";


                        console.log(
                            "Foto del profesor preparada."
                        );

                    },

                    "image/jpeg",

                    0.9
                );

            }
        );

    }


    // ======================================================
    // GUARDAR PERFIL
    // ======================================================

    if (formulario) {

        formulario.addEventListener(
            "submit",
            async (evento) => {

                evento.preventDefault();


                const apiUrl =
                    formulario.dataset.apiUrl;

                const panelUrl =
                    formulario.dataset.panelUrl;


                const datos = {

                    nombre:
                        document
                            .getElementById("nombre")
                            .value
                            .trim(),

                    apellido:
                        document
                            .getElementById("apellido")
                            .value
                            .trim(),

                    telefono:
                        document
                            .getElementById("telefono")
                            .value
                            .trim(),

                    especialidad:
                        document
                            .getElementById("especialidad")
                            .value
                            .trim()

                };


                // ==========================================
                // VALIDACIÓN
                // ==========================================

                if (
                    !datos.nombre ||
                    !datos.apellido ||
                    !datos.telefono ||
                    !datos.especialidad
                ) {

                    mensaje.textContent =
                        "Debes completar todos los campos.";

                    return;
                }


                const botonGuardar =
                    formulario.querySelector(
                        'button[type="submit"]'
                    );


                botonGuardar.disabled = true;

                botonGuardar.textContent =
                    "Guardando...";


                try {

                    // ======================================
                    // 1. ACTUALIZAR DATOS
                    // ======================================

                    const respuestaPerfil =
                        await fetch(
                            apiUrl,
                            {
                                method: "PUT",

                                credentials:
                                    "same-origin",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        datos
                                    )
                            }
                        );


                    const resultadoPerfil =
                        await respuestaPerfil.json();


                    if (!respuestaPerfil.ok) {

                        throw new Error(
                            resultadoPerfil.error ||
                            "No se pudo actualizar el perfil."
                        );

                    }


                    // ======================================
                    // 2. GUARDAR FOTO SI HAY UNA NUEVA
                    // ======================================

                    if (fotoRecortadaBlob) {

                        const formData =
                            new FormData();


                        formData.append(
                            "foto",
                            fotoRecortadaBlob,
                            "foto_perfil.jpg"
                        );


                        const respuestaFoto =
                            await fetch(
                                "/api/profesor/foto",
                                {
                                    method: "PUT",

                                    credentials:
                                        "same-origin",

                                    body:
                                        formData
                                }
                            );


                        const resultadoFoto =
                            await respuestaFoto.json();


                        if (!respuestaFoto.ok) {

                            throw new Error(
                                resultadoFoto.error ||
                                "Los datos se actualizaron, pero la foto no pudo guardarse."
                            );

                        }

                    }


                    // ======================================
                    // 3. TODO CORRECTO
                    // ======================================

                    mensaje.textContent =
                        "Perfil actualizado correctamente.";


                    setTimeout(
                        () => {

                            window.location.href =
                                panelUrl;

                        },
                        700
                    );


                } catch (error) {

                    mensaje.textContent =
                        error.message ||
                        "Ocurrió un error al actualizar el perfil.";


                    botonGuardar.disabled =
                        false;

                    botonGuardar.textContent =
                        "Guardar cambios";

                }

            }
        );

    }

})();