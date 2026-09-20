import os
from db import conectar_db
from api import api 

from services import actualizar_foto_alumno, actualizar_foto_profesor, obtener_alumno_por_usuario, obtener_profesor_por_usuario, obtener_usuario_login, obtener_clases_profesor, obtener_talleres_profesor, obtener_reserva_profesor, registrar_asistencia_reserva, obtener_alumnos_clase, obtener_talleres, obtener_taller_por_id, obtener_talleres_activos, obtener_taller_activo_por_id, obtener_planes_taller, obtener_talleres_activos_alumno, obtener_resumen_taller_alumno, contar_reservas_activas_clase, obtener_clases_disponibles_taller_alumno, obtener_inscripcion_con_saldo, obtener_clase_disponible_taller, obtener_reserva_previa_clase, crear_reserva_clase, obtener_reserva_alumno, cancelar_reserva_alumno, obtener_plan_taller, procesar_inscripcion_taller, eliminar_cuenta_profesor


from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import  check_password_hash


load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.register_blueprint(api)


# CONFIGURACIÓN PARA FOTOS DE PERFIL

CARPETA_FOTOS_PERFIL = os.path.join(
    app.root_path,
    "static",
    "img",
    "perfiles"
)

EXTENSIONES_PERMITIDAS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

def extension_permitida(nombre_archivo):

    return (
        "." in nombre_archivo
        and nombre_archivo.rsplit(".", 1)[1].lower()
        in EXTENSIONES_PERMITIDAS
    )



""" #* Prueba de conexion a la base de datos
@app.route("/prueba_db")
def prueba_db():

    conexion = conectar_db()

    if conexion.is_connected():
        mensaje = "Conexión con MySQL exitosa"
    else:
        mensaje = "No se pudo conectar con MySQL"

    conexion.close()

    return mensaje """

@app.route("/subir_foto_perfil", methods=["POST"])
def subir_foto_perfil():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

    # Verificar rol
    if session.get("rol") != "alumno":
        return "Acceso no autorizado", 403

    # Verificar que venga un archivo
    if "foto" not in request.files:
        return redirect(url_for("panel_alumno"))

    foto = request.files["foto"]

    # Verificar que se haya seleccionado una imagen
    if foto.filename == "":
        return redirect(url_for("panel_alumno"))

    # Verificar extensión
    if not extension_permitida(foto.filename):
        return "Formato de imagen no permitido", 400

    id_usuario = session["id_usuario"]

    extension = foto.filename.rsplit(".", 1)[1].lower()

    nombre_archivo = secure_filename(
        f"alumno_{id_usuario}.{extension}"
    )

    ruta_archivo = os.path.join(
        CARPETA_FOTOS_PERFIL,
        nombre_archivo
    )

    try:

        # Guardar imagen físicamente
        foto.save(ruta_archivo)

        # Actualizar MySQL mediante services.py
        actualizar_foto_alumno(
            id_usuario,
            nombre_archivo
        )

        return redirect(
            url_for("panel_alumno")
        )

    except Exception as error:

        print(
            "Error al subir foto del alumno:",
            error
        )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No se pudo actualizar la foto",
            mensaje="Ocurrió un error al guardar la foto de perfil.",
            texto_boton="Volver a mi panel",
            destino=url_for("panel_alumno")
        ), 500


@app.route("/subir_foto_profesor", methods=["POST"])
def subir_foto_profesor():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))

    # Verificar rol
    if session.get("rol") != "profesor":
        return "Acceso no autorizado", 403

    # Verificar archivo
    if "foto" not in request.files:
        return redirect(url_for("panel_profesor"))

    foto = request.files["foto"]

    # Verificar que se haya seleccionado una imagen
    if foto.filename == "":
        return redirect(url_for("panel_profesor"))

    # Validar extensión
    if not extension_permitida(foto.filename):
        return "Formato de imagen no permitido", 400

    id_usuario = session["id_usuario"]

    extension = foto.filename.rsplit(".", 1)[1].lower()

    nombre_archivo = secure_filename(
        f"profesor_{id_usuario}.{extension}"
    )

    ruta_archivo = os.path.join(
        CARPETA_FOTOS_PERFIL,
        nombre_archivo
    )

    try:

        # Guardar imagen físicamente
        foto.save(ruta_archivo)

        # Actualizar MySQL mediante services.py
        actualizar_foto_profesor(
            id_usuario,
            nombre_archivo
        )

        return redirect(
            url_for("panel_profesor")
        )

    except Exception as error:

        print(
            "Error al subir foto del profesor:",
            error
        )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No se pudo actualizar la foto",
            mensaje="Ocurrió un error al guardar la foto de perfil.",
            texto_boton="Volver a mi panel",
            destino=url_for("panel_profesor")
        ), 500


@app.route("/")
def inicio():

    foto_perfil = None

    if "id_usuario" in session:

        id_usuario = session["id_usuario"]
        rol = session.get("rol")

        if rol == "alumno":

            alumno = obtener_alumno_por_usuario(
                id_usuario
            )

            if alumno:
                foto_perfil = alumno["foto_perfil"]

        elif rol == "profesor":

            profesor = obtener_profesor_por_usuario(
                id_usuario
            )

            if profesor:
                foto_perfil = profesor["foto_perfil"]

    return render_template(
        "index.html",
        foto_perfil=foto_perfil
    )


@app.route("/seleccionar_perfil")
def seleccionar_perfil():
    return render_template("seleccionar_perfil.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")


@app.route("/comunidad")
def comunidad():
    return render_template("comunidad.html")


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


# =========================
# LOGIN ALUMNO
# =========================

@app.route("/login_alumno", methods=["GET", "POST"])
def login_alumno():

    if request.method == "POST":

        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        # Buscar usuario mediante services.py
        usuario = obtener_usuario_login(
            correo,
            "alumno"
        )

        # Verificar contraseña
        if usuario and check_password_hash(
            usuario["contrasena"],
            contrasena
        ):

            session["id_usuario"] = usuario["id_usuario"]
            session["rol"] = usuario["rol"]

            return redirect(
                url_for("panel_alumno")
            )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Datos incorrectos",
            mensaje="El correo o la contraseña ingresados no son correctos.",
            texto_boton="Volver a intentar",
            destino=url_for("login_alumno")
        )

    return render_template(
        "login_alumno.html"
    )


@app.route("/panel_alumno")
def panel_alumno():

    # Verificar que exista una sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    # Verificar que el usuario sea alumno
    if session.get("rol") != "alumno":
        return "Acceso no autorizado", 403

    # Obtener usuario conectado
    id_usuario = session["id_usuario"]

    # Obtener alumno mediante services.py
    alumno = obtener_alumno_por_usuario(
        id_usuario
    )

    if not alumno:
        return "No se encontraron los datos del alumno", 404

    return render_template(
        "panel_alumno.html",
        alumno=alumno
    )



@app.route("/editar_perfil_alumno")
def editar_perfil_alumno():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    # Verificar rol
    if session.get("rol") != "alumno":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para acceder a esta sección.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        ), 403

    id_usuario = session["id_usuario"]

    # Obtener alumno mediante services.py
    alumno = obtener_alumno_por_usuario(
        id_usuario
    )

    if not alumno:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Datos no encontrados",
            mensaje="No se encontraron los datos del alumno.",
            texto_boton="Volver",
            destino=url_for("panel_alumno")
        ), 404

    return render_template(
        "editar_perfil_alumno.html",
        alumno=alumno
    )

@app.route("/cerrar_sesion")
def cerrar_sesion():

    rol = session.get("rol")

    session.clear()

    if rol == "profesor":
        return redirect(url_for("login_profesor")) #Cerrar sesion de profesor y redirigir a login de profesor

    return redirect(url_for("login_alumno")) 


# =========================
# LOGIN PROFESOR
# =========================

@app.route("/login_profesor", methods=["GET", "POST"])
def login_profesor():

    if request.method == "POST":

        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        # Buscar usuario mediante services.py
        usuario = obtener_usuario_login(
            correo,
            "profesor"
        )

        # Verificar contraseña
        if usuario and check_password_hash(
            usuario["contrasena"],
            contrasena
        ):

            session["id_usuario"] = usuario["id_usuario"]
            session["rol"] = usuario["rol"]

            return redirect(
                url_for("panel_profesor")
            )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Datos incorrectos",
            mensaje="El correo o la contraseña ingresados no son correctos.",
            texto_boton="Volver a intentar",
            destino=url_for("login_profesor")
        )

    return render_template(
        "login_profesor.html"
    )

# =========================
# PANEL PROFESOR
# =========================

@app.route("/panel_profesor")
def panel_profesor():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return "Acceso no autorizado", 403

    # Obtener profesor mediante services.py
    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return "No se encontraron los datos del profesor", 404

    # Obtener clases mediante services.py
    clases = obtener_clases_profesor(
        profesor["id_profesor"]
    )

    return render_template(
        "panel_profesor.html",
        profesor=profesor,
        clases=clases
    )
# =========================
# EDITAR PROFESOR
# =========================
@app.route("/editar_perfil_profesor")
def editar_perfil_profesor():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para acceder a esta sección.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        ), 403

    # Obtener profesor mediante services.py
    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Datos no encontrados",
            mensaje="No se encontraron los datos del profesor.",
            texto_boton="Volver",
            destino=url_for("panel_profesor")
        ), 404

    return render_template(
        "editar_perfil_profesor.html",
        profesor=profesor
    )


@app.route("/eliminar_cuenta_profesor", methods=["POST"])
def eliminar_cuenta_profesor_ruta():

    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))

    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para realizar esta acción.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )


    id_usuario = session["id_usuario"]


    try:

        eliminado = eliminar_cuenta_profesor(id_usuario)

        if not eliminado:

            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Cuenta no encontrada",
                mensaje="No fue posible encontrar la cuenta del profesor.",
                texto_boton="Volver al panel",
                destino=url_for("panel_profesor")
            )


        session.clear()


        return render_template(
            "mensaje.html",
            tipo="exito",
            titulo="Cuenta eliminada",
            mensaje="Tu cuenta de profesor fue eliminada correctamente.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )


    except Exception:

        app.logger.exception(
            "Error al eliminar cuenta de profesor"
        )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No se pudo eliminar la cuenta",
            mensaje="Ocurrió un problema al intentar eliminar tu cuenta.",
            texto_boton="Volver al panel",
            destino=url_for("panel_profesor")
        )

@app.route("/mis_clases")
def mis_clases():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return "Acceso no autorizado", 403

    # Obtener profesor
    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return "Profesor no encontrado", 404

    # Obtener talleres del profesor
    talleres = obtener_talleres_profesor(
        profesor["id_profesor"]
    )

    # Obtener clases del profesor
    clases = obtener_clases_profesor(
        profesor["id_profesor"]
    )

    # Agrupar las clases dentro de cada taller
    for taller in talleres:

        taller["clases"] = [
            clase
            for clase in clases
            if clase["id_taller"] == taller["id_taller"]
        ]

    return render_template(
        "mis_talleres_profesor.html",
        talleres=talleres
    )



@app.route("/profesor/clase/<int:id_clase>/editar", methods=["GET"])
def editar_clase(id_clase):

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return "Acceso no autorizado", 403

    # Obtener profesor conectado
    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return "Profesor no encontrado", 404

    # Obtener todas las clases pertenecientes al profesor
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

    # Si la clase no pertenece al profesor
    # o no existe
    if not clase:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Clase no encontrada",
            mensaje="No puedes editar esta clase.",
            texto_boton="Volver a mis talleres",
            destino=url_for("mis_clases")
        )

    return render_template(
        "editar_clase.html",
        clase=clase
    )

@app.route(
    "/asistencia/reserva/<int:id_reserva>",
    methods=["POST"]
)
def registrar_asistencia(id_reserva):

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para registrar asistencia.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    # Obtener estado enviado por el formulario
    estado_asistencia = request.form.get("estado")

    if estado_asistencia not in ["presente", "ausente"]:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Estado no válido",
            mensaje="El estado de asistencia recibido no es válido.",
            texto_boton="Volver al panel",
            destino=url_for("panel_profesor")
        )

    try:

        # Obtener profesor conectado
        profesor = obtener_profesor_por_usuario(
            session["id_usuario"]
        )

        if not profesor:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Profesor no encontrado",
                mensaje="No encontramos tu perfil de profesor.",
                texto_boton="Volver al panel",
                destino=url_for("panel_profesor")
            )

        # Verificar que la reserva pertenezca
        # a una clase del profesor
        reserva = obtener_reserva_profesor(
            id_reserva,
            profesor["id_profesor"]
        )

        if not reserva:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Reserva no encontrada",
                mensaje="La reserva no existe o no pertenece a uno de tus talleres.",
                texto_boton="Volver a mis clases",
                destino=url_for("mis_clases")
            )

        # Verificar que la reserva siga activa
        if reserva["estado_reserva"] != "reservada":
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Reserva no activa",
                mensaje="Esta reserva ya no se encuentra activa.",
                texto_boton="Volver a la clase",
                destino=url_for(
                    "alumnos_clase",
                    id_clase=reserva["id_clase"]
                )
            )

        # Registrar o actualizar asistencia
        registrar_asistencia_reserva(
            id_reserva,
            profesor["id_profesor"],
            estado_asistencia
        )

        return redirect(
            url_for(
                "alumnos_clase",
                id_clase=reserva["id_clase"]
            )
        )
    except Exception as error:

        app.logger.exception(
            "Error al registrar asistencia: %s",
            error
        )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No pudimos registrar la asistencia",
            mensaje="Ocurrió un error al guardar la asistencia.",
            texto_boton="Volver a mis clases",
            destino=url_for("mis_clases")
        )


@app.route("/clase/<int:id_clase>/alumnos")
def alumnos_clase(id_clase):

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return "Acceso no autorizado", 403

    # Obtener profesor conectado
    profesor = obtener_profesor_por_usuario(
        session["id_usuario"]
    )

    if not profesor:
        return "Profesor no encontrado", 404

    # Obtener las clases pertenecientes al profesor
    clases = obtener_clases_profesor(
        profesor["id_profesor"]
    )

    # Buscar la clase solicitada dentro de sus clases
    clase = next(
        (
            clase
            for clase in clases
            if clase["id_clase"] == id_clase
        ),
        None
    )

    if not clase:
        return "Clase no encontrada o acceso no autorizado", 404

    # Obtener alumnos, reservas y asistencias
    alumnos = obtener_alumnos_clase(
        id_clase
    )

    # Calcular alumnos con reserva activa
    total_inscritos = sum(
        1
        for alumno in alumnos
        if alumno["estado_reserva"] == "reservada"
    )

    # Calcular alumnos presentes
    total_presentes = sum(
        1
        for alumno in alumnos
        if alumno["estado_reserva"] == "reservada"
        and alumno["asistencia"] == "presente"
    )

    return render_template(
        "alumnos_clase.html",
        clase=clase,
        alumnos=alumnos,
        total_inscritos=total_inscritos,
        total_presentes=total_presentes
    )

# =========================
# REGISTRO ALUMNO
# =========================

@app.route("/registro_alumno")
def registro_alumno():

    return render_template("registro_alumno.html")


# =========================
# REGLAMENTOS
# =========================

@app.route("/reglamentos", methods=["GET", "POST"])
def reglamentos():
    return render_template("reglamentos.html")

# -----------------------------------------
#     Panel de usuario 
#     distribuidor según el rol de usuario 
@app.route("/mi_panel")
def mi_panel():

    # Si no existe una sesión, enviar a selección de perfil
    if "id_usuario" not in session:
        return redirect(url_for("seleccionar_perfil"))

    # Si es alumno
    if session.get("rol") == "alumno":
        return redirect(url_for("panel_alumno"))

    # Si es profesor
    if session.get("rol") == "profesor":
        return redirect(url_for("panel_profesor"))

    # Por seguridad, si existe un rol desconocido
    session.clear()

    return redirect(url_for("seleccionar_perfil"))


#----------------------------------------------------
# TALLERES
#----------------------------------------------------
@app.route("/gestion_talleres")
def gestion_talleres():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para gestionar talleres.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    # Obtener talleres mediante services.py
    talleres = obtener_talleres()

    return render_template(
        "gestion_talleres.html",
        talleres=talleres
    )

@app.route("/crear_taller", methods=["GET"])
def crear_taller():

    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))

    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para crear talleres.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    return render_template("crear_taller.html")


@app.route("/editar_taller/<int:id_taller>", methods=["GET"])
def editar_taller(id_taller):

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_profesor")
        )

    # Verificar rol
    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para editar talleres.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    # Obtener taller mediante services.py
    taller = obtener_taller_por_id(
        id_taller
    )

    if not taller:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Taller no encontrado",
            mensaje="El taller solicitado no existe.",
            texto_boton="Volver a gestión de talleres",
            destino=url_for("gestion_talleres")
        )

    return render_template(
        "editar_taller.html",
        taller=taller
    )


@app.route("/talleres_disponibles")
def talleres_disponibles():

    """    # Verificar sesión
        if "id_usuario" not in session:
            return redirect(
                url_for("login_alumno")
            )

        # Verificar rol
        if session.get("rol") != "alumno":
            return "Acceso no autorizado"  """

    # Obtener solamente talleres activos desde services.py
    talleres = obtener_talleres_activos()

    return render_template(
        "talleres_disponibles.html",
        talleres=talleres
    )



@app.route("/taller/<int:id_taller>/planes")
def planes_taller(id_taller):

    """# Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    # Verificar rol
    if session.get("rol") != "alumno":
        return "Acceso no autorizado" """

    # Obtener taller activo mediante services.py
    taller = obtener_taller_activo_por_id(
        id_taller
    )

    # Verificar que el taller exista y esté activo
    if not taller:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Taller no disponible",
            mensaje="Este taller no existe o actualmente se encuentra desactivado.",
            texto_boton="Volver a talleres",
            destino=url_for("talleres_disponibles")
        )

    # Obtener planes del taller mediante services.py
    planes = obtener_planes_taller(
        id_taller
    )

    return render_template(
        "planes_taller.html",
        taller=taller,
        planes=planes
    )


@app.route("/taller/<int:id_taller>/plan/<int:id_plan>/confirmar")
def confirmar_inscripcion(id_taller, id_plan):

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    # Verificar rol
    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    # Obtener plan mediante services.py
    datos = obtener_plan_taller(
        id_taller,
        id_plan
    )

    if not datos:
        return "El plan seleccionado no corresponde a este taller"

    return render_template(
        "confirmar_inscripcion.html",
        datos=datos
    )


@app.route(
    "/taller/<int:id_taller>/plan/<int:id_plan>/inscribir",
    methods=["POST"]
)
def inscribir_taller(id_taller, id_plan):

    # =====================================================
    # 1. VERIFICAR SESIÓN
    # =====================================================

    if "id_usuario" not in session:

        return redirect(
            url_for("login_alumno")
        )


    # =====================================================
    # 2. VERIFICAR ROL
    # =====================================================

    if session.get("rol") != "alumno":

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para realizar esta acción.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )


    # =====================================================
    # 3. PROCESAR INSCRIPCIÓN
    # =====================================================

    try:

        resultado = procesar_inscripcion_taller(
            session["id_usuario"],
            id_taller,
            id_plan
        )


        # =================================================
        # ALUMNO NO ENCONTRADO
        # =================================================

        if resultado["resultado"] == "alumno_no_encontrado":

            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Alumno no encontrado",
                mensaje="No se pudo encontrar tu registro de alumno.",
                texto_boton="Volver al inicio",
                destino=url_for("inicio")
            )


        # =================================================
        # PLAN NO VÁLIDO
        # =================================================

        if resultado["resultado"] == "plan_no_valido":

            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Plan no válido",
                mensaje="El plan seleccionado no corresponde a este taller.",
                texto_boton="Volver a talleres",
                destino=url_for(
                    "talleres_disponibles"
                )
            )


        # =================================================
        # MENSUALIDAD EXISTENTE
        # =================================================

        if resultado["resultado"] == "mensual_existente":

            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Ya estás inscrito",
                mensaje="Ya tienes una mensualidad activa en este taller.",
                texto_boton="Ir a mis talleres",
                destino=url_for("mis_talleres")
            )


        # =================================================
        # CLASE SUELTA AGREGADA
        # =================================================

        if resultado["resultado"] == "clase_agregada":

            return render_template(
                "mensaje.html",
                tipo="exito",
                titulo="Clase agregada",
                mensaje=(
                    "La nueva clase suelta fue agregada "
                    "correctamente a tu inscripción."
                ),
                texto_boton="Ir a mis talleres",
                destino=url_for("mis_talleres")
            )


        # =================================================
        # NUEVA INSCRIPCIÓN
        # =================================================

        if resultado["resultado"] == "inscripcion_creada":

            if resultado["tipo"] == "suelta":

                mensaje = (
                    "La clase suelta fue contratada correctamente. "
                    "Puedes contratar más clases sueltas si lo deseas."
                )

            else:

                mensaje = (
                    "Tu inscripción mensual fue realizada correctamente."
                )


            return render_template(
                "mensaje.html",
                tipo="exito",
                titulo="Inscripción realizada",
                mensaje=mensaje,
                texto_boton="Ir a mis talleres",
                destino=url_for("mis_talleres")
            )


    # =====================================================
    # 4. ERROR
    # =====================================================

    except Exception as error:

        print(
            "Error al realizar inscripción:",
            error
        )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No pudimos realizar la inscripción",
            mensaje="Ocurrió un error al procesar tu inscripción.",
            texto_boton="Volver a talleres",
            destino=url_for(
                "talleres_disponibles"
            )
        )

@app.route("/mis_talleres")
def mis_talleres():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    # Verificar rol
    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    id_usuario = session["id_usuario"]

    # Obtener talleres agrupados del alumno
    inscripciones = obtener_talleres_activos_alumno(
        id_usuario
    )

    return render_template(
        "mis_talleres.html",
        inscripciones=inscripciones
    )

@app.route("/taller/<int:id_taller>/mis_clases")
def clases_disponibles_taller(id_taller):

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    # Verificar rol
    if session.get("rol") != "alumno":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para acceder a esta sección.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    id_usuario = session["id_usuario"]

    # Obtener resumen del taller y saldo de clases
    resumen = obtener_resumen_taller_alumno(
        id_usuario,
        id_taller
    )

    # El alumno no tiene una inscripción activa
    # en este taller
    if not resumen:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Taller no encontrado",
            mensaje=(
                "No tienes una inscripción activa "
                "en este taller."
            ),
            texto_boton="Volver a mis talleres",
            destino=url_for("mis_talleres")
        )

    # Obtener clases futuras del taller
    clases = obtener_clases_disponibles_taller_alumno(
        id_usuario,
        id_taller
    )

    return render_template(
        "clases_disponibles_alumno.html",
        inscripcion=resumen,
        clases=clases,
        clases_usadas=resumen["clases_usadas"],
        clases_disponibles=resumen["clases_disponibles"]
    )

@app.route(
    "/taller/<int:id_taller>/clase/<int:id_clase>/reservar",
    methods=["POST"]
)
def reservar_clase_taller(id_taller, id_clase):

    # ====================================================
    # 1. Verificar sesión y rol
    # ====================================================

    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    if session.get("rol") != "alumno":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para reservar clases.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    id_usuario = session["id_usuario"]


    # ====================================================
    # 2. Verificar saldo total del taller
    # ====================================================

    resumen = obtener_resumen_taller_alumno(
        id_usuario,
        id_taller
    )

    if not resumen:
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Taller no disponible",
            mensaje="No tienes una inscripción activa en este taller.",
            texto_boton="Volver a mis talleres",
            destino=url_for("mis_talleres")
        )

    if resumen["clases_disponibles"] <= 0:
        return render_template(
            "mensaje.html",
            tipo="aviso",
            titulo="Sin clases disponibles",
            mensaje="Ya utilizaste todas las clases que tienes contratadas.",
            texto_boton="Volver a mis clases",
            destino=url_for(
                "clases_disponibles_taller",
                id_taller=id_taller
            )
        )


    # ====================================================
    # 3. Buscar una inscripción que todavía tenga saldo
    # ====================================================

    inscripcion = obtener_inscripcion_con_saldo(
        id_usuario,
        id_taller
    )

    if not inscripcion:
        return render_template(
            "mensaje.html",
            tipo="aviso",
            titulo="Sin saldo disponible",
            mensaje=(
                "No se encontró una inscripción con "
                "clases disponibles para realizar la reserva."
            ),
            texto_boton="Volver a mis clases",
            destino=url_for(
                "clases_disponibles_taller",
                id_taller=id_taller
            )
        )


    # ====================================================
    # 4. Validar clase y crear reserva
    # ====================================================

    try:

        # ====================================================
        # Verificar que la clase:
        # - pertenezca al taller
        # - esté programada
        # - todavía no haya comenzado
        # ====================================================

        clase = obtener_clase_disponible_taller(
            id_clase,
            id_taller
        )

        if not clase:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Clase no disponible",
                mensaje=(
                    "La clase seleccionada no existe, "
                    "ya comenzó o no está disponible."
                ),
                texto_boton="Volver a mis clases",
                destino=url_for(
                    "clases_disponibles_taller",
                    id_taller=id_taller
                )
            )


        # ====================================================
        # 5. Verificar si el alumno ya reservó esta clase
        # ====================================================

        reserva_existente = obtener_reserva_previa_clase(
            id_usuario,
            id_clase
        )


        # ====================================================
        # Ya tiene una reserva activa
        # ====================================================

        if (
            reserva_existente
            and reserva_existente["estado"] == "reservada"
        ):

            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Clase ya reservada",
                mensaje=(
                    "Ya tienes una reserva activa "
                    "para esta clase."
                ),
                texto_boton="Volver a mis clases",
                destino=url_for(
                    "clases_disponibles_taller",
                    id_taller=id_taller
                )
            )


        # ====================================================
        # Ya reservó y canceló esta clase anteriormente
        # ====================================================

        if (
            reserva_existente
            and reserva_existente["estado"] == "cancelada"
        ):

            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Reserva cancelada anteriormente",
                mensaje=(
                    "Ya cancelaste anteriormente esta clase. "
                    "No puedes volver a reservar el mismo horario."
                ),
                texto_boton="Volver a mis clases",
                destino=url_for(
                    "clases_disponibles_taller",
                    id_taller=id_taller
                )
            )


        # ====================================================
        # 6. Verificar cupos
        # ====================================================

        reservados = contar_reservas_activas_clase(
            id_clase
        )

        if reservados >= clase["cupo_maximo"]:

            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Clase completa",
                mensaje="Esta clase ya no tiene cupos disponibles.",
                texto_boton="Volver a mis clases",
                destino=url_for(
                    "clases_disponibles_taller",
                    id_taller=id_taller
                )
            )


        # ====================================================
        # 7. Crear la reserva
        # ====================================================

        crear_reserva_clase(
            inscripcion["id_inscripcion"],
            id_clase
        )


        # ====================================================
        # 8. Reserva realizada
        # ====================================================

        return render_template(
            "mensaje.html",
            tipo="exito",
            titulo="Clase reservada",
            mensaje="Tu clase fue reservada correctamente.",
            texto_boton="Volver a mis clases",
            destino=url_for(
                "clases_disponibles_taller",
                id_taller=id_taller
            )
        )


    # ====================================================
    # 9. Manejo de errores
    # ====================================================

    except Exception as error:

        print(
            "Error al reservar clase:",
            error
        )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No pudimos realizar la reserva",
            mensaje="Ocurrió un error al intentar reservar la clase.",
            texto_boton="Volver a mis clases",
            destino=url_for(
                "clases_disponibles_taller",
                id_taller=id_taller
            )
        )


@app.route(
    "/reserva/<int:id_reserva>/cancelar",
    methods=["POST"]
)
def cancelar_reserva(id_reserva):

    # ====================================================
    # 1. Verificar sesión y rol
    # ====================================================

    if "id_usuario" not in session:
        return redirect(
            url_for("login_alumno")
        )

    if session.get("rol") != "alumno":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para realizar esta acción.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    id_usuario = session["id_usuario"]


    # ====================================================
    # 2. Verificar que la reserva pertenezca al alumno
    # ====================================================

    try:

        reserva = obtener_reserva_alumno(
            id_reserva,
            id_usuario
        )

        if not reserva:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Reserva no encontrada",
                mensaje=(
                    "No encontramos esta reserva "
                    "o no tienes acceso a ella."
                ),
                texto_boton="Volver a mis talleres",
                destino=url_for("mis_talleres")
            )


        # ====================================================
        # 3. Verificar que la reserva siga activa
        # ====================================================

        if reserva["estado"] != "reservada":
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Reserva no activa",
                mensaje="Esta reserva ya no se encuentra activa.",
                texto_boton="Volver a mis talleres",
                destino=url_for("mis_talleres")
            )


        # ====================================================
        # 4. Cancelar reserva
        #
        # 2 horas o más:
        #     recupera el crédito
        #
        # Menos de 2 horas:
        #     consume el crédito
        # ====================================================

        cancelada = cancelar_reserva_alumno(
            id_reserva
        )

        if not cancelada:
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="No se pudo cancelar",
                mensaje=(
                    "La reserva ya no se encuentra activa "
                    "o no pudo ser cancelada."
                ),
                texto_boton="Volver a mis clases",
                destino=url_for(
                    "clases_disponibles_taller",
                    id_taller=reserva["id_taller"]
                )
            )


        # ====================================================
        # 5. Volver a las clases del taller
        # ====================================================

        return redirect(
            url_for(
                "clases_disponibles_taller",
                id_taller=reserva["id_taller"]
            )
        )


    # ====================================================
    # 6. Manejo de errores
    # ====================================================

    except Exception as error:

        print(
            "Error al cancelar reserva:",
            error
        )

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No pudimos cancelar la reserva",
            mensaje="Ocurrió un error al intentar cancelar la clase.",
            texto_boton="Volver a mis talleres",
            destino=url_for("mis_talleres")
        )






# =========================
# API TALLERES FINAL CÓDIGO 
# =========================



# =========================
# ANALISIS DE DATOS  
# =========================

# FUNCIONES NUEVAS PARA ESTADISTICAS DEL ALUMNO
@app.route("/mis_estadisticas")
def mis_estadisticas():
    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))
    if session.get("rol") != "alumno":
        return "Acceso no autorizado", 403
    return render_template("mis_estadisticas.html")



# FUNCIONES NUEVAS PARA ESTADISTICAS DEL PROFESOR 

# =========================================
# ESTADÍSTICAS DEL PROFESOR
# =========================================

@app.route("/mis_estadisticas_profesor")
def mis_estadisticas_profesor():

    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))

    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para acceder a esta sección.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

    return render_template(
        "mis_estadisticas_profesor.html"
    )




if __name__ == "__main__":
    app.run(debug=True) 


"""if __name__ == "__main__": 

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    ) """