from flask import Blueprint, jsonify, session, request, current_app
import mysql.connector
from werkzeug.security import generate_password_hash
from db import conectar_db
import os
import uuid
from services import obtener_taller_por_id, obtener_talleres, crear_taller, actualizar_taller, eliminar_taller, obtener_clases_profesor, obtener_profesor_por_usuario, obtener_talleres_profesor, profesor_tiene_taller,  crear_clase, actualizar_clase, cancelar_clase, eliminar_clase, correo_usuario_existe, rut_alumno_existe, crear_alumno, obtener_alumno_por_usuario,actualizar_perfil_alumno, actualizar_foto_alumno, actualizar_perfil_profesor, actualizar_foto_profesor, obtener_alumno_por_usuario, obtener_profesor_por_usuario, eliminar_cuenta_alumno, obtener_estadisticas_alumno, obtener_clases_taller_api

# ============================================================
# BLUEPRINT API RESt
# ============================================================

api = Blueprint("api", __name__)




# ==========================================================
# API REST - LISTAR TALLERES
# ==========================================================

@api.route("/api/talleres", methods=["GET"])
def api_listar_talleres():

    if "id_usuario" not in session:
        return jsonify({
            "error": "No autenticado"
        }), 401

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "Acceso no autorizado"
        }), 403

    talleres = obtener_talleres()

    return jsonify({
        "talleres": talleres
    }), 200

# ==========================================================
# API REST - CREAR TALLER
# ==========================================================

@api.route("/api/talleres", methods=["POST"])
def api_crear_taller():

    # Verificar sesión
    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # Verificar rol
    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para crear talleres."
        }), 403

    # --------------------------------------------------
    # RECIBIR JSON
    # --------------------------------------------------

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Debes enviar los datos del taller."
        }), 400

    nombre = str(datos.get("nombre", "")).strip()
    descripcion = str(datos.get("descripcion", "")).strip()
    horario = str(datos.get("horario", "")).strip()
    imagen = str(datos.get("imagen", "")).strip()

    cupo_maximo = datos.get("cupo_maximo")

    # --------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------

    if not nombre:
        return jsonify({
            "error": "El nombre del taller es obligatorio."
        }), 400

    try:
        cupo_maximo = int(cupo_maximo)

        if cupo_maximo < 1:
            raise ValueError

    except (TypeError, ValueError):

        return jsonify({
            "error": "El cupo máximo debe ser un número mayor a 0."
        }), 400

    # --------------------------------------------------
    # SERVICIO
    # --------------------------------------------------

    try:

        taller = crear_taller(
            nombre,
            descripcion,
            horario,
            cupo_maximo,
            imagen
        )

        return jsonify({
            "mensaje": "Taller creado correctamente.",
            "taller": taller
        }), 201

    except mysql.connector.Error as error:

        print("Error al crear taller:", error)

        return jsonify({
            "error": "No se pudo crear el taller."
        }), 500


# ==========================================================
# API REST - OBTENER UN TALLER
# ==========================================================

@api.route("/api/talleres/<int:id_taller>", methods=["GET"])
def obtener_taller(id_taller):

    if "id_usuario" not in session:
        return jsonify({
            "error": "No autenticado"
        }), 401

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "Acceso no autorizado"
        }), 403

    taller = obtener_taller_por_id(id_taller)  # SEPARACION DE ROLES (SERVICES.APY)

    if not taller:
        return jsonify({
            "error": "Taller no encontrado"
        }), 404

    return jsonify({
        "taller": taller
    }), 200

# ==========================================================
# API REST - ACTUALIZAR TALLER
# ==========================================================

@api.route("/api/talleres/<int:id_taller>", methods=["PUT"])
def api_actualizar_taller(id_taller):

    # Verificar sesión
    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # Verificar rol
    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para editar talleres."
        }), 403

    # --------------------------------------------------
    # RECIBIR JSON
    # --------------------------------------------------

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Debes enviar los datos del taller."
        }), 400

    nombre = str(datos.get("nombre", "")).strip()
    descripcion = str(datos.get("descripcion", "")).strip()
    horario = str(datos.get("horario", "")).strip()
    imagen = str(datos.get("imagen", "")).strip()

    cupo_maximo = datos.get("cupo_maximo")

    # --------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------

    if not nombre:
        return jsonify({
            "error": "El nombre del taller es obligatorio."
        }), 400

    try:
        cupo_maximo = int(cupo_maximo)

        if cupo_maximo < 1:
            raise ValueError

    except (TypeError, ValueError):

        return jsonify({
            "error": "El cupo máximo debe ser mayor a 0."
        }), 400

    # --------------------------------------------------
    # COMPROBAR QUE EL TALLER EXISTE
    # --------------------------------------------------

    taller_existente = obtener_taller_por_id(id_taller)

    if not taller_existente:
        return jsonify({
            "error": "El taller no existe."
        }), 404

    # --------------------------------------------------
    # ACTUALIZAR MEDIANTE SERVICES
    # --------------------------------------------------

    try:

        taller = actualizar_taller(
            id_taller,
            nombre,
            descripcion,
            horario,
            cupo_maximo,
            imagen
        )

        return jsonify({
            "mensaje": "Taller actualizado correctamente.",
            "taller": taller
        }), 200

    except mysql.connector.Error as error:

        print("Error al actualizar taller:", error)

        return jsonify({
            "error": "No se pudo actualizar el taller."
        }), 500


# ==========================================================
# API REST - ELIMINAR TALLER
# ==========================================================

@api.route("/api/talleres/<int:id_taller>", methods=["DELETE"])
def api_eliminar_taller(id_taller):

    # Verificar sesión
    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # Verificar rol
    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para eliminar talleres."
        }), 403

    # --------------------------------------------------
    # COMPROBAR QUE EL TALLER EXISTE
    # --------------------------------------------------

    taller = obtener_taller_por_id(id_taller)

    if not taller:
        return jsonify({
            "error": "El taller no existe."
        }), 404

    # --------------------------------------------------
    # ELIMINAR MEDIANTE SERVICES
    # --------------------------------------------------

    try:

        eliminar_taller(id_taller)

        return jsonify({
            "mensaje": "Taller eliminado permanentemente.",
            "id_taller": id_taller
        }), 200

    except mysql.connector.IntegrityError:

        return jsonify({
            "error":
                "No se puede eliminar este taller porque tiene "
                "registros relacionados."
        }), 409

    except mysql.connector.Error as error:

        print("Error al eliminar taller:", error)

        return jsonify({
            "error": "No se pudo eliminar el taller."
        }), 500


@api.route(
    "/api/talleres/<int:id_taller>/clases",
    methods=["GET"]
)
def api_clases_taller(id_taller):

    if "id_usuario" not in session:

        return jsonify({
            "error": "No autenticado"
        }), 401


    if session.get("rol") != "profesor":

        return jsonify({
            "error": "Acceso no autorizado"
        }), 403


    try:

        resultado = obtener_clases_taller_api(
            id_taller
        )


        if not resultado:

            return jsonify({
                "error": {
                    "codigo": "taller_no_encontrado",
                    "mensaje": "El taller solicitado no existe."
                }
            }), 404


        return jsonify(
            resultado
        ), 200


    except mysql.connector.Error:

        print(
            "Error al consultar las clases del taller"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudieron consultar las clases."
            }
        }), 500

# ==========================================================
# API REST - CREAR CLASE
# ==========================================================

@api.route("/api/talleres/<int:id_taller>/clases", methods=["POST"])
def api_crear_clase(id_taller):

    # --------------------------------------------------
    # VERIFICAR SESIÓN
    # --------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # --------------------------------------------------
    # VERIFICAR ROL
    # --------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para crear clases."
        }), 403

    # --------------------------------------------------
    # RECIBIR JSON
    # --------------------------------------------------

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Debes enviar los datos de la clase."
        }), 400

    fecha = str(datos.get("fecha", "")).strip()
    hora_inicio = str(datos.get("hora_inicio", "")).strip()
    hora_fin = str(datos.get("hora_fin", "")).strip()
    cupo_maximo = datos.get("cupo_maximo")

    # --------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------

    if not fecha or not hora_inicio or not hora_fin:
        return jsonify({
            "error":
                "Fecha, hora de inicio y hora de fin son obligatorias."
        }), 400

    try:

        cupo_maximo = int(cupo_maximo)

        if cupo_maximo < 1:
            raise ValueError

    except (TypeError, ValueError):

        return jsonify({
            "error": "El cupo máximo debe ser mayor a 0."
        }), 400

    if hora_fin <= hora_inicio:
        return jsonify({
            "error":
                "La hora de término debe ser posterior a la hora de inicio."
        }), 400

    # --------------------------------------------------
    # OBTENER PROFESOR
    # --------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return jsonify({
            "error": "No se encontró el perfil del profesor."
        }), 404

    id_profesor = profesor["id_profesor"]

    # --------------------------------------------------
    # COMPROBAR ASIGNACIÓN DEL TALLER
    # --------------------------------------------------

    if not profesor_tiene_taller(
        id_profesor,
        id_taller
    ):
        return jsonify({
            "error": "Este taller no está asignado a tu perfil."
        }), 403

    # --------------------------------------------------
    # CREAR CLASE
    # --------------------------------------------------

    try:

        clase = crear_clase(
            id_taller,
            fecha,
            hora_inicio,
            hora_fin,
            cupo_maximo
        )

        return jsonify({
            "mensaje": "Clase creada correctamente.",
            "clase": clase
        }), 201

    except mysql.connector.Error as error:

        print("Error al crear clase:", error)

        return jsonify({
            "error": "No se pudo crear la clase."
        }), 500

# ==========================================================
# API REST - LISTAR CLASES DEL PROFESOR
# ==========================================================

@api.route("/api/clases", methods=["GET"])
def api_listar_clases():

    # --------------------------------------------------
    # VERIFICAR SESIÓN
    # --------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # --------------------------------------------------
    # VERIFICAR ROL
    # --------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para ver las clases."
        }), 403

    # --------------------------------------------------
    # OBTENER PROFESOR
    # --------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return jsonify({
            "error": "No se encontró el profesor."
        }), 404

    id_profesor = profesor["id_profesor"]

    # --------------------------------------------------
    # OBTENER TALLERES DEL PROFESOR
    # --------------------------------------------------

    talleres = obtener_talleres_profesor(
        id_profesor
    )

    # --------------------------------------------------
    # OBTENER CLASES DEL PROFESOR
    # --------------------------------------------------

    clases = obtener_clases_profesor(
        id_profesor
    )

    # --------------------------------------------------
    # AGRUPAR CLASES POR TALLER
    # --------------------------------------------------

    resultado = []

    for taller in talleres:

        clases_taller = [
            clase
            for clase in clases
            if clase["id_taller"] == taller["id_taller"]
        ]

        resultado.append({
            "id_taller": taller["id_taller"],
            "taller": taller["nombre"],
            "clases": clases_taller
        })

    # --------------------------------------------------
    # RESPUESTA
    # --------------------------------------------------

    return jsonify({
        "talleres": resultado
    }), 200

# ==========================================================
# API REST - ACTUALIZAR CLASE
# ==========================================================

@api.route("/api/clases/<int:id_clase>", methods=["PUT"])
def api_actualizar_clase(id_clase):

    # --------------------------------------------------
    # VERIFICAR SESIÓN
    # --------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # --------------------------------------------------
    # VERIFICAR ROL
    # --------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para editar clases."
        }), 403

    # --------------------------------------------------
    # RECIBIR JSON
    # --------------------------------------------------

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Debes enviar los datos de la clase."
        }), 400

    fecha = str(datos.get("fecha", "")).strip()
    hora_inicio = str(datos.get("hora_inicio", "")).strip()
    hora_fin = str(datos.get("hora_fin", "")).strip()
    cupo_maximo = datos.get("cupo_maximo")

    # --------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------

    if not fecha or not hora_inicio or not hora_fin:
        return jsonify({
            "error":
                "Fecha, hora de inicio y hora de fin son obligatorias."
        }), 400

    try:

        cupo_maximo = int(cupo_maximo)

        if cupo_maximo < 1:
            raise ValueError

    except (TypeError, ValueError):

        return jsonify({
            "error": "El cupo máximo debe ser mayor a 0."
        }), 400

    if hora_fin <= hora_inicio:
        return jsonify({
            "error":
                "La hora de término debe ser posterior a la hora de inicio."
        }), 400

    # --------------------------------------------------
    # OBTENER PROFESOR
    # --------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return jsonify({
            "error": "No se encontró el perfil del profesor."
        }), 404

    # --------------------------------------------------
    # VERIFICAR CLASE Y PERMISOS
    # --------------------------------------------------

    clase = obtener_clases_profesor(
        id_clase,
        profesor["id_profesor"]
    )

    if not clase:
        return jsonify({
            "error":
                "La clase no existe o no pertenece a uno de tus talleres."
        }), 404

    # --------------------------------------------------
    # ACTUALIZAR CLASE
    # --------------------------------------------------

    try:

        clase_actualizada = actualizar_clase(
            id_clase,
            fecha,
            hora_inicio,
            hora_fin,
            cupo_maximo
        )

        # Agregamos el taller que ya obtuvimos anteriormente
        clase_actualizada["id_taller"] = clase["id_taller"]

        return jsonify({
            "mensaje": "Clase actualizada correctamente.",
            "clase": clase_actualizada
        }), 200

    except mysql.connector.Error as error:

        print("Error al actualizar clase:", error)

        return jsonify({
            "error": "No se pudo actualizar la clase."
        }), 500


# ==========================================================
# API REST - CANCELAR CLASE
# ==========================================================

@api.route("/api/clases/<int:id_clase>/cancelar", methods=["PUT"])
def api_cancelar_clase(id_clase):

    # --------------------------------------------------
    # VERIFICAR SESIÓN
    # --------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # --------------------------------------------------
    # VERIFICAR ROL
    # --------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para cancelar clases."
        }), 403

    # --------------------------------------------------
    # OBTENER PROFESOR
    # --------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return jsonify({
            "error": "No se encontró el perfil del profesor."
        }), 404

    # --------------------------------------------------
    # OBTENER CLASES DEL PROFESOR
    # --------------------------------------------------

    clases = obtener_clases_profesor(
        profesor["id_profesor"]
    )

    # Buscar la clase solicitada
    clase = next(
        (
            clase
            for clase in clases
            if clase["id_clase"] == id_clase
        ),
        None
    )

    # --------------------------------------------------
    # VERIFICAR CLASE Y PERMISOS
    # --------------------------------------------------

    if not clase:
        return jsonify({
            "error":
                "La clase no existe o no pertenece a uno de tus talleres."
        }), 404

    # --------------------------------------------------
    # EVITAR DOBLE CANCELACIÓN
    # --------------------------------------------------

    if clase["estado"] == "cancelada":
        return jsonify({
            "error": "Esta clase ya se encuentra cancelada."
        }), 409

    # --------------------------------------------------
    # CANCELAR CLASE
    # --------------------------------------------------

    try:

        resultado = cancelar_clase(id_clase)

        return jsonify({
            "mensaje": "Clase cancelada correctamente.",
            "id_clase": resultado["id_clase"],
            "estado": resultado["estado"],
            "reservas_canceladas":
                resultado["reservas_canceladas"]
        }), 200

    except mysql.connector.Error as error:

        print("Error al cancelar clase:", error)

        return jsonify({
            "error": "No se pudo cancelar la clase."
        }), 500

# ==========================================================
# API REST - ELIMINAR CLASE FÍSICAMENTE
# ==========================================================

@api.route("/api/clases/<int:id_clase>", methods=["DELETE"])
def api_eliminar_clase(id_clase):

    # --------------------------------------------------
    # VERIFICAR SESIÓN
    # --------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # --------------------------------------------------
    # VERIFICAR ROL
    # --------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "No tienes permisos para eliminar clases."
        }), 403

    # --------------------------------------------------
    # OBTENER PROFESOR
    # --------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return jsonify({
            "error": "No se encontró el perfil del profesor."
        }), 404

    # --------------------------------------------------
    # OBTENER CLASES DEL PROFESOR
    # --------------------------------------------------

    clases = obtener_clases_profesor(
        profesor["id_profesor"]
    )

    # Buscar la clase solicitada
    clase = next(
        (
            clase
            for clase in clases
            if clase["id_clase"] == id_clase
        ),
        None
    )

    # --------------------------------------------------
    # VERIFICAR CLASE Y PERMISOS
    # --------------------------------------------------

    if not clase:
        return jsonify({
            "error":
                "La clase no existe o no pertenece a uno de tus talleres."
        }), 404

    # --------------------------------------------------
    # ELIMINAR CLASE
    # --------------------------------------------------

    try:

        eliminar_clase(id_clase)

        return jsonify({
            "mensaje": "Clase eliminada permanentemente.",
            "id_clase": id_clase
        }), 200

    except mysql.connector.IntegrityError:

        return jsonify({
            "error":
                "No se puede eliminar esta clase porque tiene "
                "reservas o registros relacionados. Puedes cancelarla "
                "para conservar su historial."
        }), 409

    except mysql.connector.Error as error:

        print("Error al eliminar clase:", error)

        return jsonify({
            "error": "No se pudo eliminar la clase."
        }), 500

# ==========================================================
# API REST - CREAR ALUMNO
# ==========================================================

@api.route("/api/alumnos", methods=["POST"])
def api_crear_alumno():

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Debes enviar los datos del alumno."
        }), 400

    # ------------------------------------------------------
    # RECIBIR DATOS
    # ------------------------------------------------------

    nombre = str(datos.get("nombre", "")).strip()
    apellido = str(datos.get("apellido", "")).strip()
    rut = str(datos.get("rut", "")).strip()

    fecha_nacimiento = str(
        datos.get("fecha_nacimiento", "")
    ).strip()

    correo = str(datos.get("correo", "")).strip()
    telefono = str(datos.get("telefono", "")).strip()

    contacto_emergencia = str(
        datos.get("contacto_emergencia", "")
    ).strip()

    telefono_emergencia = str(
        datos.get("telefono_emergencia", "")
    ).strip()

    contrasena = str(datos.get("contrasena", ""))

    confirmar_contrasena = str(
        datos.get("confirmar_contrasena", "")
    )

    acepta_condiciones = datos.get(
        "acepta_condiciones",
        False
    )

    # ------------------------------------------------------
    # VALIDACIONES
    # ------------------------------------------------------

    if (
        not nombre
        or not apellido
        or not rut
        or not fecha_nacimiento
        or not correo
        or not contrasena
    ):
        return jsonify({
            "error": "Debes completar los campos obligatorios."
        }), 400

    if contrasena != confirmar_contrasena:
        return jsonify({
            "error": "Las contraseñas no coinciden."
        }), 400

    if not acepta_condiciones:
        return jsonify({
            "error":
                "Debes aceptar el reglamento y las condiciones "
                "de La Maestranza."
        }), 400

    # ------------------------------------------------------
    # COMPROBAR CORREO
    # ------------------------------------------------------

    if correo_usuario_existe(correo):
        return jsonify({
            "error": "El correo ingresado ya está registrado."
        }), 409

    # ------------------------------------------------------
    # COMPROBAR RUT
    # ------------------------------------------------------

    if rut_alumno_existe(rut):
        return jsonify({
            "error": "El RUT ingresado ya está registrado."
        }), 409

    # ------------------------------------------------------
    # HASH DE CONTRASEÑA
    # ------------------------------------------------------

    contrasena_hash = generate_password_hash(
        contrasena
    )

    # ------------------------------------------------------
    # CREAR ALUMNO MEDIANTE SERVICES
    # ------------------------------------------------------

    try:

        alumno = crear_alumno(
            correo,
            contrasena_hash,
            nombre,
            apellido,
            rut,
            fecha_nacimiento,
            telefono,
            contacto_emergencia,
            telefono_emergencia
        )

        return jsonify({
            "mensaje": "Alumno registrado correctamente.",
            "alumno": alumno
        }), 201

    except mysql.connector.Error as error:

        print("Error al registrar alumno:", error)

        return jsonify({
            "error": "No se pudo registrar el alumno."
        }), 500


# ==========================================================
# API REST - OBTENER PERFIL DEL ALUMNO
# ==========================================================

@api.route("/api/alumno/perfil", methods=["GET"])
def api_obtener_perfil_alumno():

    # ------------------------------------------------------
    # VERIFICAR SESIÓN
    # ------------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # ------------------------------------------------------
    # VERIFICAR ROL
    # ------------------------------------------------------

    if session.get("rol") != "alumno":
        return jsonify({
            "error": "Acceso no autorizado."
        }), 403

    # ------------------------------------------------------
    # OBTENER ALUMNO MEDIANTE SERVICES
    # ------------------------------------------------------

    alumno = obtener_alumno_por_usuario(
        session["id_usuario"]
    )

    if not alumno:
        return jsonify({
            "error": "No se encontraron los datos del alumno."
        }), 404

    # ------------------------------------------------------
    # RESPUESTA
    # ------------------------------------------------------

    return jsonify({
        "alumno": alumno
    }), 200


# ==========================================================
# API REST - ACTUALIZAR PERFIL DEL ALUMNO
# ==========================================================

@api.route("/api/alumno/perfil", methods=["PUT"])
def api_actualizar_perfil_alumno():

    # ------------------------------------------------------
    # VERIFICAR SESIÓN
    # ------------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # ------------------------------------------------------
    # VERIFICAR ROL
    # ------------------------------------------------------

    if session.get("rol") != "alumno":
        return jsonify({
            "error": "Acceso no autorizado."
        }), 403

    # ------------------------------------------------------
    # RECIBIR JSON
    # ------------------------------------------------------

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Debes enviar los datos del alumno."
        }), 400

    nombre = str(datos.get("nombre", "")).strip()
    apellido = str(datos.get("apellido", "")).strip()
    telefono = str(datos.get("telefono", "")).strip()

    contacto_emergencia = str(
        datos.get("contacto_emergencia", "")
    ).strip()

    telefono_emergencia = str(
        datos.get("telefono_emergencia", "")
    ).strip()

    # ------------------------------------------------------
    # VALIDACIONES
    # ------------------------------------------------------

    if (
        not nombre
        or not apellido
        or not telefono
        or not contacto_emergencia
        or not telefono_emergencia
    ):
        return jsonify({
            "error": "Debes completar todos los campos."
        }), 400

    id_usuario = session["id_usuario"]

    # ------------------------------------------------------
    # COMPROBAR QUE EL ALUMNO EXISTE
    # ------------------------------------------------------

    alumno = obtener_alumno_por_usuario(id_usuario)

    if not alumno:
        return jsonify({
            "error": "No se encontraron los datos del alumno."
        }), 404

    # ------------------------------------------------------
    # ACTUALIZAR MEDIANTE SERVICES
    # ------------------------------------------------------

    try:

        datos_actualizados = actualizar_perfil_alumno(
            id_usuario,
            nombre,
            apellido,
            telefono,
            contacto_emergencia,
            telefono_emergencia
        )

        datos_actualizados["id_alumno"] = alumno["id_alumno"]

        return jsonify({
            "mensaje": "Datos personales actualizados correctamente.",
            "alumno": datos_actualizados
        }), 200

    except mysql.connector.Error as error:

        print("Error al actualizar perfil:", error)

        return jsonify({
            "error": "No se pudieron actualizar los datos."
        }), 500





# ==========================================================
# API REST - ELIMINAR CUENTA DEL ALUMNO
# ==========================================================

@api.route("/api/alumno/cuenta", methods=["DELETE"])
def api_eliminar_cuenta_alumno():

    # ------------------------------------------------------
    # VERIFICAR SESIÓN
    # ------------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # ------------------------------------------------------
    # VERIFICAR ROL
    # ------------------------------------------------------

    if session.get("rol") != "alumno":
        return jsonify({
            "error": "Acceso no autorizado."
        }), 403

    id_usuario = session["id_usuario"]

    # ------------------------------------------------------
    # ELIMINAR CUENTA MEDIANTE SERVICES
    # ------------------------------------------------------

    try:

        cuenta_eliminada = eliminar_cuenta_alumno(
            id_usuario
        )

        if not cuenta_eliminada:
            return jsonify({
                "error": "No se encontró la cuenta del alumno."
            }), 404

        # Cerrar la sesión después de eliminar la cuenta
        session.clear()

        return jsonify({
            "mensaje": "Cuenta eliminada correctamente."
        }), 200

    except mysql.connector.Error as error:

        print(
            "Error al eliminar cuenta:",
            error
        )

        return jsonify({
            "error": "No se pudo eliminar la cuenta."
        }), 500

# ============================================================
# GUARDAR FOTO PERFIL ALUMNO
# ============================================================

@api.route("/api/alumno/foto", methods=["PUT"])
def api_actualizar_foto_alumno():

    # --------------------------------------------------
    # VERIFICAR SESIÓN
    # --------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # --------------------------------------------------
    # VERIFICAR ROL
    # --------------------------------------------------

    if session.get("rol") != "alumno":
        return jsonify({
            "error": "Acceso no autorizado."
        }), 403

    id_usuario = session["id_usuario"]

    # --------------------------------------------------
    # RECIBIR FOTO
    # --------------------------------------------------

    foto = request.files.get("foto")

    if not foto:
        return jsonify({
            "error": "No se recibió ninguna imagen."
        }), 400

    # --------------------------------------------------
    # VALIDAR EXTENSIÓN
    # --------------------------------------------------

    extensiones_permitidas = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    if "." not in foto.filename:
        return jsonify({
            "error": "Archivo no válido."
        }), 400

    extension = (
        foto.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    if extension not in extensiones_permitidas:
        return jsonify({
            "error": "Formato de imagen no permitido."
        }), 400

    # --------------------------------------------------
    # OBTENER ALUMNO MEDIANTE SERVICES
    # --------------------------------------------------

    alumno = obtener_alumno_por_usuario(
        id_usuario
    )

    if not alumno:
        return jsonify({
            "error": "Alumno no encontrado."
        }), 404

    try:

        # --------------------------------------------------
        # GENERAR NOMBRE ÚNICO
        # --------------------------------------------------

        nombre_archivo = (
            f"alumno_{alumno['id_alumno']}_"
            f"{uuid.uuid4().hex}.jpg"
        )

        # --------------------------------------------------
        # CARPETA DE PERFILES
        # --------------------------------------------------

        carpeta_perfiles = os.path.join(
            current_app.root_path,
            "static",
            "img",
            "perfiles"
        )

        os.makedirs(
            carpeta_perfiles,
            exist_ok=True
        )

        ruta_archivo = os.path.join(
            carpeta_perfiles,
            nombre_archivo
        )

        # --------------------------------------------------
        # GUARDAR ARCHIVO
        # --------------------------------------------------

        foto.save(ruta_archivo)

        # --------------------------------------------------
        # ACTUALIZAR BASE DE DATOS MEDIANTE SERVICES
        # --------------------------------------------------

        actualizar_foto_alumno(
            id_usuario,
            nombre_archivo
        )

        return jsonify({
            "mensaje": "Foto actualizada correctamente.",
            "foto_perfil": nombre_archivo
        }), 200

    except Exception as error:

        print(
            "Error al actualizar foto:",
            error
        )

        return jsonify({
            "error": "No se pudo actualizar la foto."
        }), 500

    
# ==========================================================
# API REST - OBTENER PERFIL DEL PROFESOR
# ==========================================================

@api.route("/api/profesor/perfil", methods=["GET"])
def api_obtener_perfil_profesor():

    # ------------------------------------------------------
    # VERIFICAR SESIÓN
    # ------------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # ------------------------------------------------------
    # VERIFICAR ROL
    # ------------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "Acceso no autorizado."
        }), 403

    # ------------------------------------------------------
    # OBTENER PROFESOR MEDIANTE SERVICES
    # ------------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return jsonify({
            "error": "Profesor no encontrado."
        }), 404

    # ------------------------------------------------------
    # RESPUESTA
    # ------------------------------------------------------

    return jsonify({
        "profesor": profesor
    }), 200

# ==========================================================
# API REST - ACTUALIZAR PERFIL DEL PROFESOR
# ==========================================================

@api.route("/api/profesor/perfil", methods=["PUT"])
def api_actualizar_perfil_profesor():

    # ------------------------------------------------------
    # VERIFICAR SESIÓN
    # ------------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # ------------------------------------------------------
    # VERIFICAR ROL
    # ------------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "Acceso no autorizado."
        }), 403

    # ------------------------------------------------------
    # RECIBIR JSON
    # ------------------------------------------------------

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "No se recibieron datos."
        }), 400

    nombre = str(
        datos.get("nombre", "")
    ).strip()

    apellido = str(
        datos.get("apellido", "")
    ).strip()

    telefono = str(
        datos.get("telefono", "")
    ).strip()

    especialidad = str(
        datos.get("especialidad", "")
    ).strip()

    # ------------------------------------------------------
    # VALIDAR CAMPOS
    # ------------------------------------------------------

    if (
        not nombre
        or not apellido
        or not telefono
        or not especialidad
    ):
        return jsonify({
            "error": "Debes completar todos los campos."
        }), 400

    id_usuario = session["id_usuario"]

    # ------------------------------------------------------
    # COMPROBAR QUE EL PROFESOR EXISTE
    # ------------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        id_usuario
    )

    if not profesor:
        return jsonify({
            "error": "Profesor no encontrado."
        }), 404

    # ------------------------------------------------------
    # ACTUALIZAR MEDIANTE SERVICES
    # ------------------------------------------------------

    try:

        datos_actualizados = actualizar_perfil_profesor(
            id_usuario,
            nombre,
            apellido,
            telefono,
            especialidad
        )

        datos_actualizados["id_profesor"] = (
            profesor["id_profesor"]
        )

        return jsonify({
            "mensaje": "Perfil actualizado correctamente.",
            "profesor": datos_actualizados
        }), 200

    except mysql.connector.Error as error:

        print(
            "Error al actualizar perfil del profesor:",
            error
        )

        return jsonify({
            "error": "No se pudo actualizar el perfil."
        }), 500


# ==========================================================
# API REST - ACTUALIZAR FOTO DEL PROFESOR
# ==========================================================

@api.route("/api/profesor/foto", methods=["PUT"])
def api_actualizar_foto_profesor():

    # ------------------------------------------------------
    # VERIFICAR SESIÓN
    # ------------------------------------------------------

    if "id_usuario" not in session:
        return jsonify({
            "error": "Debes iniciar sesión."
        }), 401

    # ------------------------------------------------------
    # VERIFICAR ROL
    # ------------------------------------------------------

    if session.get("rol") != "profesor":
        return jsonify({
            "error": "Acceso no autorizado."
        }), 403

    id_usuario = session["id_usuario"]

    # ------------------------------------------------------
    # RECIBIR FOTO
    # ------------------------------------------------------

    foto = request.files.get("foto")

    if not foto:
        return jsonify({
            "error": "No se recibió ninguna imagen."
        }), 400

    # ------------------------------------------------------
    # VALIDAR EXTENSIÓN
    # ------------------------------------------------------

    extensiones_permitidas = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    if "." not in foto.filename:
        return jsonify({
            "error": "Archivo no válido."
        }), 400

    extension = (
        foto.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    if extension not in extensiones_permitidas:
        return jsonify({
            "error": "Formato de imagen no permitido."
        }), 400

    # ------------------------------------------------------
    # OBTENER PROFESOR MEDIANTE SERVICES
    # ------------------------------------------------------

    profesor = obtener_profesor_por_usuario(
        id_usuario
    )

    if not profesor:
        return jsonify({
            "error": "Profesor no encontrado."
        }), 404

    try:

        # --------------------------------------------------
        # GENERAR NOMBRE ÚNICO
        # --------------------------------------------------

        nombre_archivo = (
            f"profesor_{profesor['id_profesor']}_"
            f"{uuid.uuid4().hex}.jpg"
        )

        # --------------------------------------------------
        # CARPETA DE PERFILES
        # --------------------------------------------------

        carpeta_perfiles = os.path.join(
            current_app.root_path,
            "static",
            "img",
            "perfiles"
        )

        os.makedirs(
            carpeta_perfiles,
            exist_ok=True
        )

        ruta_archivo = os.path.join(
            carpeta_perfiles,
            nombre_archivo
        )

        # --------------------------------------------------
        # GUARDAR ARCHIVO
        # --------------------------------------------------

        foto.save(ruta_archivo)

        # --------------------------------------------------
        # ACTUALIZAR BD MEDIANTE SERVICES
        # --------------------------------------------------

        actualizar_foto_profesor(
            id_usuario,
            nombre_archivo
        )

        return jsonify({
            "mensaje": "Foto actualizada correctamente.",
            "foto_perfil": nombre_archivo
        }), 200

    except Exception as error:

        print(
            "Error al actualizar foto del profesor:",
            error
        )

        return jsonify({
            "error": "No se pudo actualizar la foto."
        }), 500



# ==========================================================
# API REST - ESTADISTICAS
# ==========================================================

# --------------------------------------------------
# API ESTADISTICAS ALUMNO
# --------------------------------------------------

@api.route("/api/alumno/estadisticas", methods=["GET"])
def api_alumno_estadisticas():

    if "id_usuario" not in session:
        return jsonify({
            "error": {
                "mensaje":
                    "Inicia sesión para consultar tus estadísticas."
            }
        }), 401

    if session.get("rol") != "alumno":
        return jsonify({
            "error": {
                "mensaje":
                    "Acceso exclusivo para alumnos."
            }
        }), 403

    try:

        resultado = obtener_estadisticas_alumno(
            session["id_usuario"]
        )

        if not resultado:
            return jsonify({
                "error": {
                    "mensaje":
                        "No se encontró tu perfil de alumno."
                }
            }), 404

        respuesta = jsonify(resultado)

        respuesta.headers["Cache-Control"] = "no-store"

        return respuesta, 200

    except mysql.connector.Error:

        print(
            "Error al consultar estadísticas del alumno"
        )

        return jsonify({
            "error": {
                "mensaje":
                    "No se pudieron cargar tus estadísticas. "
                    "Intenta nuevamente."
            }
        }), 500


# ============================================================
# API - ESTADÍSTICAS DEL PROFESOR
# ============================================================

@api.route("/api/profesor/estadisticas", methods=["GET"])
def estadisticas_profesor():

    # Verificar que exista una sesión
    if "id_usuario" not in session:
        return jsonify({
            "error": "No has iniciado sesión"
        }), 401

    # Verificar que el usuario sea profesor
    if session.get("rol") != "profesor":
        return jsonify({
            "error": "Acceso no autorizado"
        }), 403

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # ====================================================
        # OBTENER PROFESOR CONECTADO
        # ====================================================

        cursor.execute("""
            SELECT id_profesor
            FROM profesores
            WHERE id_usuario = %s
        """, (session["id_usuario"],))

        profesor = cursor.fetchone()

        if not profesor:
            return jsonify({
                "error": "Profesor no encontrado"
            }), 404

        id_profesor = profesor["id_profesor"]


        # ====================================================
        # 1. TALLERES ASIGNADOS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(DISTINCT id_taller) AS total
            FROM taller_profesor
            WHERE id_profesor = %s
        """, (id_profesor,))

        talleres_asignados = cursor.fetchone()["total"]


        # ====================================================
        # 2. ALUMNOS ACTIVOS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(DISTINCT i.id_alumno) AS total

            FROM inscripciones i

            INNER JOIN taller_profesor tp
                ON i.id_taller = tp.id_taller

            WHERE tp.id_profesor = %s
            AND i.estado = 'activa'
        """, (id_profesor,))

        alumnos_activos = cursor.fetchone()["total"]


        # ====================================================
        # 3. RESERVAS ACTIVAS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM reservas_clase r

            INNER JOIN clases c
                ON r.id_clase = c.id_clase

            INNER JOIN taller_profesor tp
                ON c.id_taller = tp.id_taller

            WHERE tp.id_profesor = %s
            AND r.estado = 'reservada'
        """, (id_profesor,))

        reservas_activas = cursor.fetchone()["total"]


        # ====================================================
        # 4. RESERVAS CANCELADAS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM reservas_clase r

            INNER JOIN clases c
                ON r.id_clase = c.id_clase

            INNER JOIN taller_profesor tp
                ON c.id_taller = tp.id_taller

            WHERE tp.id_profesor = %s
            AND r.estado = 'cancelada'
        """, (id_profesor,))

        reservas_canceladas = cursor.fetchone()["total"]


        # ====================================================
        # 5. ESTADÍSTICAS POR TALLER
        # ====================================================

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre,

                COUNT(DISTINCT CASE
                    WHEN i.estado = 'activa'
                    THEN i.id_alumno
                END) AS alumnos_activos,

                COUNT(DISTINCT CASE
                    WHEN r.estado = 'reservada'
                    THEN r.id_reserva
                END) AS reservas_activas,

                COUNT(DISTINCT CASE
                    WHEN r.estado = 'cancelada'
                    THEN r.id_reserva
                END) AS reservas_canceladas

            FROM talleres t

            INNER JOIN taller_profesor tp
                ON t.id_taller = tp.id_taller

            LEFT JOIN inscripciones i
                ON t.id_taller = i.id_taller

            LEFT JOIN clases c
                ON t.id_taller = c.id_taller

            LEFT JOIN reservas_clase r
                ON c.id_clase = r.id_clase

            WHERE tp.id_profesor = %s

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY t.nombre
        """, (id_profesor,))

        talleres = cursor.fetchall()


        # ====================================================
        # 6. CALCULAR OCUPACIÓN POR TALLER
        # ====================================================

        

        for taller in talleres:

            cursor.execute("""
                SELECT

                    (
                        SELECT COALESCE(SUM(c.cupo_maximo), 0)
                        FROM clases c
                        WHERE c.id_taller = %s
                        AND c.estado = 'programada'
                        AND c.fecha >= CURDATE()
                    ) AS cupos_totales,

                    (
                        SELECT COUNT(*)
                        FROM reservas_clase r
                        INNER JOIN clases c
                            ON r.id_clase = c.id_clase
                        WHERE c.id_taller = %s
                        AND c.estado = 'programada'
                        AND c.fecha >= CURDATE()
                        AND r.estado = 'reservada'
                    ) AS reservas

            """, (
                taller["id_taller"],
                taller["id_taller"]
            ))

            ocupacion = cursor.fetchone()

            cupos_totales = ocupacion["cupos_totales"] or 0
            reservas = ocupacion["reservas"] or 0

            if cupos_totales > 0:
                porcentaje_ocupacion = round(
                    (reservas / cupos_totales) * 100,
                    1
                )
            else:
                porcentaje_ocupacion = 0

            taller["ocupacion"] = porcentaje_ocupacion

            # Calcular asistencia del taller
            cursor.execute("""
                SELECT
                    COUNT(CASE
                        WHEN a.estado = 'presente'
                        THEN 1
                    END) AS presentes,

                    COUNT(CASE
                        WHEN a.estado = 'ausente'
                        THEN 1
                    END) AS ausentes

                FROM asistencias a

                INNER JOIN reservas_clase r
                    ON a.id_reserva = r.id_reserva

                INNER JOIN clases c
                    ON r.id_clase = c.id_clase

                WHERE c.id_taller = %s
            """, (taller["id_taller"],))

            datos_asistencia = cursor.fetchone()

            presentes = datos_asistencia["presentes"] or 0
            ausentes = datos_asistencia["ausentes"] or 0

            total_asistencias = presentes + ausentes

            if total_asistencias > 0:

                porcentaje_asistencia = round(
                    (presentes / total_asistencias) * 100,
                    1
                )

            else:

                porcentaje_asistencia = 0

            taller["asistencia"] = porcentaje_asistencia
            taller["presentes"] = presentes
            taller["ausentes"] = ausentes
        # ====================================================
        # RESPUESTA JSON
        # ====================================================

        return jsonify({

            "talleres_asignados": talleres_asignados,

            "alumnos_activos": alumnos_activos,

            "reservas_activas": reservas_activas,

            "reservas_canceladas": reservas_canceladas,

            "talleres": talleres

        })


    except mysql.connector.Error as error:

        print("Error API estadísticas:", error)

        return jsonify({
            "error": "Error al obtener las estadísticas"
        }), 500


    finally:

        cursor.close()
        conexion.close()


