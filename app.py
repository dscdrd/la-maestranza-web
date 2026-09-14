import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector 

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


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


#* Conexion a la base de datos SQL
def conectar_db():

    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return conexion


#* Prueba de conexion a la base de datos
@app.route("/prueba_db")
def prueba_db():

    conexion = conectar_db()

    if conexion.is_connected():
        mensaje = "Conexión con MySQL exitosa"
    else:
        mensaje = "No se pudo conectar con MySQL"

    conexion.close()

    return mensaje

@app.route("/subir_foto_perfil", methods=["POST"])
def subir_foto_perfil():

    # Verificar sesión
    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

    # Verificar rol
    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    # Verificar que venga un archivo
    if "foto" not in request.files:
        return redirect(url_for("panel_alumno"))

    foto = request.files["foto"]

    # Verificar que se haya seleccionado una imagen
    if foto.filename == "":
        return redirect(url_for("panel_alumno"))

    # Verificar extensión
    if not extension_permitida(foto.filename):
        return "Formato de imagen no permitido"

    id_usuario = session["id_usuario"]

    extension = foto.filename.rsplit(".", 1)[1].lower()

    nombre_archivo = secure_filename(
        f"alumno_{id_usuario}.{extension}"
    )

    ruta_archivo = os.path.join(
        CARPETA_FOTOS_PERFIL,
        nombre_archivo
    )

    # Guardar imagen
    foto.save(ruta_archivo)

    # Guardar nombre en MySQL
    conexion = conectar_db()
    cursor = conexion.cursor()

    sql = """
        UPDATE alumnos
        SET foto_perfil = %s
        WHERE id_usuario = %s
    """

    cursor.execute(
        sql,
        (nombre_archivo, id_usuario)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for("panel_alumno"))


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

    # Guardar imagen
    foto.save(ruta_archivo)

    # Actualizar base de datos
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE profesores
            SET foto_perfil = %s
            WHERE id_usuario = %s
        """, (
            nombre_archivo,
            id_usuario
        ))

        conexion.commit()

    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for("panel_profesor"))


@app.route("/")
def inicio():

    foto_perfil = None

    if "id_usuario" in session:

        id_usuario = session["id_usuario"]
        rol = session.get("rol")

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        try:

            if rol == "alumno":

                cursor.execute("""
                    SELECT foto_perfil
                    FROM alumnos
                    WHERE id_usuario = %s
                """, (id_usuario,))

                usuario = cursor.fetchone()

                if usuario:
                    foto_perfil = usuario["foto_perfil"]


            elif rol == "profesor":

                cursor.execute("""
                    SELECT foto_perfil
                    FROM profesores
                    WHERE id_usuario = %s
                """, (id_usuario,))

                usuario = cursor.fetchone()

                if usuario:
                    foto_perfil = usuario["foto_perfil"]

        finally:
            cursor.close()
            conexion.close()

    return render_template(
        "index.html",
        foto_perfil=foto_perfil
    )

@app.route("/talleres")
def talleres():
    return render_template("talleres.html")


@app.route("/registro")
def registro():
    return render_template("registro.html")


@app.route("/seleccionar_perfil")
def seleccionar_perfil():
    return render_template("seleccionar_perfil.html")


@app.route("/equipo")
def equipo():
    return render_template("equipo.html")


@app.route("/Terapias")
def terapias():
    return render_template("terapias.html")


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

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT *
            FROM usuarios
            WHERE correo = %s AND rol = %s
        """

        cursor.execute(sql, (correo, "alumno"))

        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario and check_password_hash(
            usuario["contrasena"],
            contrasena
        ):

            # Guardamos al usuario que inició sesión
            session["id_usuario"] = usuario["id_usuario"]
            session["rol"] = usuario["rol"]

            # Lo enviamos a su panel
            return redirect(url_for("panel_alumno"))

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Datos incorrectos",
            mensaje="El correo o la contraseña ingresados no son correctos.",
            texto_boton="Volver a intentar",
            destino=url_for("login_alumno")
        )

    return render_template("login_alumno.html")


@app.route("/panel_alumno")
def panel_alumno():

    # Verificar que exista una sesión
    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

    # Verificar que el usuario sea alumno
    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    # Obtener el id del usuario conectado
    id_usuario = session["id_usuario"]

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM alumnos
        WHERE id_usuario = %s
    """

    cursor.execute(sql, (id_usuario,))

    alumno = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not alumno:
        return "No se encontraron los datos del alumno"

    return render_template(
        "panel_alumno.html",
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

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT *
            FROM usuarios
            WHERE correo = %s AND rol = %s
        """

        cursor.execute(sql, (correo, "profesor"))

        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario and check_password_hash(
            usuario["contrasena"],
            contrasena
        ):

            session["id_usuario"] = usuario["id_usuario"]
            session["rol"] = usuario["rol"]

            return redirect(url_for("panel_profesor"))

        return "Correo o contraseña incorrectos"

    return render_template("login_profesor.html")

# =========================
# PANEL PROFESOR
# =========================

@app.route("/panel_profesor")
def panel_profesor():
    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))
    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="Esta sección está disponible solo para profesores.",
            texto_boton="Volver a mi panel",
            destino=url_for("mi_panel")
        ), 403
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM profesores WHERE id_usuario = %s", (session["id_usuario"],))
        profesor = cursor.fetchone()
        if not profesor:
            return "Profesor no encontrado", 404
        cursor.execute("""
        SELECT
            c.id_clase,
            c.fecha,
            c.hora_inicio,
            c.hora_fin,
            c.cupo_maximo,
            c.estado,
            t.id_taller,
            t.nombre AS taller,

            (
                SELECT COUNT(*)
                FROM reservas_clase r
                WHERE r.id_clase = c.id_clase
                AND r.estado = 'reservada'
            ) AS reservados

        FROM clases c

        INNER JOIN talleres t
            ON c.id_taller = t.id_taller

        WHERE EXISTS (
            SELECT 1 FROM taller_profesor tp
            WHERE tp.id_taller = t.id_taller AND tp.id_profesor = %s
        )
        AND c.fecha = CURDATE()

        ORDER BY c.fecha, c.hora_inicio
    """, (profesor["id_profesor"],))
        clases_hoy = cursor.fetchall()
        return render_template("panel_profesor.html", profesor=profesor, clases_hoy=clases_hoy)
    finally:
        cursor.close()
        conexion.close()


@app.route("/mis_clases")
def mis_clases():
    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))
    if session.get("rol") != "profesor":
        return "Acceso no autorizado", 403
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_profesor FROM profesores WHERE id_usuario = %s", (session["id_usuario"],))
        profesor = cursor.fetchone()
        if not profesor:
            return "Profesor no encontrado", 404
        cursor.execute("""
            SELECT t.id_taller, t.nombre, t.horario
            FROM talleres t
            WHERE EXISTS (
                SELECT 1 FROM taller_profesor tp
                WHERE tp.id_taller = t.id_taller AND tp.id_profesor = %s
            )
            ORDER BY t.nombre
        """, (profesor["id_profesor"],))
        talleres = cursor.fetchall()
        cursor.execute("""
        SELECT
            c.id_clase,
            c.fecha,
            c.hora_inicio,
            c.hora_fin,
            c.cupo_maximo,
            c.estado,
            t.id_taller,
            t.nombre AS taller,

            (
                SELECT COUNT(*)
                FROM reservas_clase r
                WHERE r.id_clase = c.id_clase
                AND r.estado = 'reservada'
            ) AS reservados

        FROM clases c

        INNER JOIN talleres t
            ON c.id_taller = t.id_taller

        WHERE EXISTS (
            SELECT 1 FROM taller_profesor tp
            WHERE tp.id_taller = t.id_taller AND tp.id_profesor = %s
        )

        ORDER BY c.fecha DESC, c.hora_inicio
    """, (profesor["id_profesor"],))
        clases = cursor.fetchall()
        for taller in talleres:
            taller["clases"] = [c for c in clases if c["id_taller"] == taller["id_taller"]]
        return render_template("mis_talleres_profesor.html", talleres=talleres)
    finally:
        cursor.close()
        conexion.close()



@app.route("/mis_clases_profesor")
def mis_clases_profesor():

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

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # Obtener profesor conectado
        cursor.execute("""
            SELECT id_profesor
            FROM profesores
            WHERE id_usuario = %s
        """, (session["id_usuario"],))

        profesor = cursor.fetchone()

        if not profesor:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Profesor no encontrado",
                mensaje="No encontramos tu perfil de profesor.",
                texto_boton="Volver al panel",
                destino=url_for("panel_profesor")
            )

        # Obtener clases de los talleres asignados
        cursor.execute("""
            SELECT
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                t.nombre AS taller,

                COUNT(
                    CASE
                        WHEN r.estado = 'reservada'
                        THEN r.id_reserva
                    END
                ) AS alumnos_reservados

            FROM clases c

            INNER JOIN talleres t
                ON c.id_taller = t.id_taller

            INNER JOIN taller_profesor tp
                ON tp.id_taller = t.id_taller

            LEFT JOIN reservas_clase r
                ON r.id_clase = c.id_clase

            WHERE tp.id_profesor = %s

            GROUP BY
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                t.nombre

            ORDER BY
                t.nombre,
                c.fecha,
                c.hora_inicio

        """, (profesor["id_profesor"],))

        clases = cursor.fetchall()


        # Agrupar clases por taller
        clases_por_taller = {}

        for clase in clases:

            nombre_taller = clase["taller"]

            if nombre_taller not in clases_por_taller:
                clases_por_taller[nombre_taller] = []

            clases_por_taller[nombre_taller].append(clase)


        return render_template(
            "mis_clases_profesor.html",
            clases_por_taller=clases_por_taller
        )

    finally:

        cursor.close()
        conexion.close()

@app.route("/asistencia/clase/<int:id_clase>")
def asistencia_clase(id_clase):

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

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # =========================================
        # OBTENER PROFESOR CONECTADO
        # =========================================

        cursor.execute("""
            SELECT
                id_profesor
            FROM profesores
            WHERE id_usuario = %s
        """, (session["id_usuario"],))

        profesor = cursor.fetchone()

        if not profesor:

            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Profesor no encontrado",
                mensaje="No encontramos tu perfil de profesor.",
                texto_boton="Volver al panel",
                destino=url_for("panel_profesor")
            )


        # =========================================
        # VERIFICAR QUE LA CLASE PERTENEZCA
        # A UN TALLER DEL PROFESOR
        # =========================================

        cursor.execute("""
            SELECT
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.estado,
                t.nombre AS taller

            FROM clases c

            INNER JOIN talleres t
                ON c.id_taller = t.id_taller

            INNER JOIN taller_profesor tp
                ON tp.id_taller = t.id_taller

            WHERE c.id_clase = %s
            AND tp.id_profesor = %s
        """, (
            id_clase,
            profesor["id_profesor"]
        ))

        clase = cursor.fetchone()


        if not clase:

            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Clase no encontrada",
                mensaje="La clase no existe o no pertenece a uno de tus talleres.",
                texto_boton="Volver a mis clases",
                destino=url_for("mis_clases_profesor")
            )


        # =========================================
        # OBTENER ALUMNOS CON RESERVA ACTIVA
        # =========================================

        cursor.execute("""
            SELECT
                r.id_reserva,

                a.id_alumno,
                a.nombre,
                a.apellido,

                asi.estado AS asistencia

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON r.id_inscripcion = i.id_inscripcion

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            LEFT JOIN asistencias asi
                ON asi.id_reserva = r.id_reserva

            WHERE r.id_clase = %s
            AND r.estado = 'reservada'

            ORDER BY
                a.apellido,
                a.nombre
        """, (id_clase,))

        alumnos = cursor.fetchall()


        return render_template(
            "asistencia_clase.html",
            clase=clase,
            alumnos=alumnos
        )


    finally:

        cursor.close()
        conexion.close()


@app.route(
    "/asistencia/reserva/<int:id_reserva>",
    methods=["POST"]
)
def registrar_asistencia(id_reserva):

    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))

    if session.get("rol") != "profesor":
        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="Acceso no autorizado",
            mensaje="No tienes permisos para registrar asistencia.",
            texto_boton="Volver al inicio",
            destino=url_for("inicio")
        )

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

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # Obtener profesor conectado
        cursor.execute("""
            SELECT id_profesor
            FROM profesores
            WHERE id_usuario = %s
        """, (session["id_usuario"],))

        profesor = cursor.fetchone()

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
        # a una clase de un taller del profesor
        cursor.execute("""
            SELECT
                r.id_reserva,
                r.id_clase,
                r.estado AS estado_reserva

            FROM reservas_clase r

            INNER JOIN clases c
                ON r.id_clase = c.id_clase

            INNER JOIN taller_profesor tp
                ON c.id_taller = tp.id_taller

            WHERE r.id_reserva = %s
            AND tp.id_profesor = %s
        """, (
            id_reserva,
            profesor["id_profesor"]
        ))

        reserva = cursor.fetchone()

        if not reserva:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Reserva no encontrada",
                mensaje="La reserva no existe o no pertenece a uno de tus talleres.",
                texto_boton="Volver a mis clases",
                destino=url_for("mis_clases_profesor")
            )


        if reserva["estado_reserva"] != "reservada":
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Reserva no activa",
                mensaje="Esta reserva ya no se encuentra activa.",
                texto_boton="Volver a la clase",
                destino=url_for(
                    "asistencia_clase",
                    id_clase=reserva["id_clase"]
                )
            )


        # Insertar o actualizar asistencia
        cursor.execute("""
            INSERT INTO asistencias (
                id_reserva,
                id_profesor,
                estado
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE               
                id_profesor = VALUES(id_profesor),
                estado = VALUES(estado),
                fecha_registro = CURRENT_TIMESTAMP
        """, (
            id_reserva,
            profesor["id_profesor"],
            estado_asistencia
        ))

        conexion.commit()

        return redirect(
            url_for(
                "asistencia_clase",
                id_clase=reserva["id_clase"]
            )
        )


    except mysql.connector.Error as error:

        conexion.rollback()

        print("Error al registrar asistencia:", error)

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No pudimos registrar la asistencia",
            mensaje="Ocurrió un error al guardar la asistencia.",
            texto_boton="Volver a mis clases",
            destino=url_for("mis_clases_profesor")
        )


    finally:

        cursor.close()
        conexion.close()




@app.route("/clase/<int:id_clase>/alumnos")
def alumnos_clase(id_clase):

    # Verificar que exista una sesión
    if "id_usuario" not in session:
        return redirect(url_for("login_profesor"))

    # Verificar que sea profesor
    if session.get("rol") != "profesor":
        return "Acceso no autorizado"

    id_usuario = session["id_usuario"]

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    # Buscar al profesor conectado
    cursor.execute("""
        SELECT id_profesor
        FROM profesores
        WHERE id_usuario = %s
    """, (id_usuario,))

    profesor = cursor.fetchone()

    if not profesor:
        cursor.close()
        conexion.close()
        return "Profesor no encontrado"

    id_profesor = profesor["id_profesor"]

    # Buscar la clase y comprobar que pertenece
    # a un taller asignado a este profesor
    cursor.execute("""
        SELECT
            c.id_clase,
            c.fecha,
            c.hora_inicio,
            c.hora_fin,
            c.cupo_maximo,
            c.estado,
            t.nombre AS taller

        FROM clases c

        INNER JOIN talleres t
            ON c.id_taller = t.id_taller

        INNER JOIN taller_profesor tp
            ON t.id_taller = tp.id_taller

        WHERE c.id_clase = %s
        AND tp.id_profesor = %s
    """, (id_clase, id_profesor))

    clase = cursor.fetchone()

    if not clase:
        cursor.close()
        conexion.close()
        return "Clase no encontrada o acceso no autorizado"

    # Obtener los alumnos de esa clase
    cursor.execute("""
        SELECT
            a.id_alumno,
            a.nombre,
            a.apellido,
            a.rut,
            r.estado,
            r.fecha_reserva,
            r.fecha_cancelacion

        FROM reservas_clase r

        INNER JOIN inscripciones i
            ON r.id_inscripcion = i.id_inscripcion

        INNER JOIN alumnos a
            ON i.id_alumno = a.id_alumno

        WHERE r.id_clase = %s

        ORDER BY a.apellido, a.nombre
    """, (id_clase,))

    alumnos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "alumnos_clase.html",
        clase=clase,
        alumnos=alumnos
    )

# =========================
# REGISTRO ALUMNO
# =========================

# =========================
# REGISTRO ALUMNO
# =========================

@app.route("/registro_alumno", methods=["GET", "POST"])
def registro_alumno():

    if request.method == "POST":

        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        rut = request.form["rut"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        correo = request.form["correo"]
        telefono = request.form["telefono"]
        contacto_emergencia = request.form["contacto_emergencia"]
        telefono_emergencia = request.form["telefono_emergencia"]

        contrasena = request.form["contrasena"]
        contrasena_confirmacion = request.form["confirmar_contrasena"]

        # Recibir checkbox de condiciones
        acepta_condiciones = request.form.get("acepta_condiciones")


        # =========================
        # VALIDAR CONTRASEÑAS
        # =========================

        if contrasena != contrasena_confirmacion:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Las contraseñas no coinciden",
                mensaje="Verifica que ambas contraseñas sean iguales e inténtalo nuevamente.",
                texto_boton="Volver al registro",
                destino=url_for("registro_alumno")
            )


        # =========================
        # VALIDAR CONDICIONES
        # =========================

        if not acepta_condiciones:
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Debes aceptar las condiciones",
                mensaje="Para registrarte debes aceptar el reglamento y las condiciones de La Maestranza.",
                texto_boton="Volver al registro",
                destino=url_for("registro_alumno")
            )


        # =========================
        # ENCRIPTAR CONTRASEÑA
        # =========================

        contrasena_hash = generate_password_hash(contrasena)

        conexion = conectar_db()
        cursor = conexion.cursor()

        try:

            # =========================
            # VALIDAR CORREO DUPLICADO
            # =========================

            sql_buscar_correo = """
                SELECT id_usuario
                FROM usuarios
                WHERE correo = %s
            """

            cursor.execute(sql_buscar_correo, (correo,))

            usuario_existente = cursor.fetchone()

            if usuario_existente:
                return render_template(
                    "mensaje.html",
                    tipo="aviso",
                    titulo="Correo ya registrado",
                    mensaje="El correo ingresado ya se encuentra asociado a una cuenta.",
                    texto_boton="Volver al registro",
                    destino=url_for("registro_alumno")
                )


            # =========================
            # VALIDAR RUT DUPLICADO
            # =========================

            sql_buscar_rut = """
                SELECT id_alumno
                FROM alumnos
                WHERE rut = %s
            """

            cursor.execute(sql_buscar_rut, (rut,))

            alumno_existente = cursor.fetchone()

            if alumno_existente:
                return render_template(
                    "mensaje.html",
                    tipo="aviso",
                    titulo="RUT ya registrado",
                    mensaje="El RUT ingresado ya se encuentra registrado.",
                    texto_boton="Volver al registro",
                    destino=url_for("registro_alumno")
                )


            # =========================
            # INSERTAR USUARIO
            # =========================

            sql_usuario = """
                INSERT INTO usuarios (
                    correo,
                    contrasena,
                    rol
                )
                VALUES (%s, %s, %s)
            """

            datos_usuario = (
                correo,
                contrasena_hash,
                "alumno"
            )

            cursor.execute(sql_usuario, datos_usuario)

            # Obtener el id_usuario creado por MySQL
            id_usuario = cursor.lastrowid


            # =========================
            # INSERTAR ALUMNO
            # =========================

            sql_alumno = """
                INSERT INTO alumnos (
                    id_usuario,
                    nombre,
                    apellido,
                    rut,
                    fecha_nacimiento,
                    telefono,
                    contacto_emergencia,
                    telefono_emergencia
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            datos_alumno = (
                id_usuario,
                nombre,
                apellido,
                rut,
                fecha_nacimiento,
                telefono,
                contacto_emergencia,
                telefono_emergencia
            )

            cursor.execute(sql_alumno, datos_alumno)


            # =========================
            # GUARDAR CAMBIOS
            # =========================

            conexion.commit()


            # =========================
            # REGISTRO EXITOSO
            # =========================

            return render_template(
                "mensaje.html",
                tipo="exito",
                titulo="Registro completado",
                mensaje="Tu cuenta de alumno fue creada correctamente.",
                texto_boton="Volver al inicio",
                destino=url_for("inicio")
            )


        except Exception as error:

            conexion.rollback()

            print("Error al registrar alumno:", error)

            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="No pudimos completar el registro",
                mensaje="Ocurrió un error al registrar tu cuenta. Inténtalo nuevamente.",
                texto_boton="Volver al registro",
                destino=url_for("registro_alumno")
            )


        finally:

            cursor.close()
            conexion.close()


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



@app.route("/talleres_disponibles")
def talleres_disponibles():

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id_taller,
            nombre,
            descripcion,
            horario,
            cupo_maximo,
            imagen
        FROM talleres
        ORDER BY nombre
    """)

    talleres = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "talleres_disponibles.html",
        talleres=talleres
    )



@app.route("/taller/<int:id_taller>/planes")
def planes_taller(id_taller):

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id_taller,
            nombre,
            descripcion,
            horario,
            cupo_maximo
        FROM talleres
        WHERE id_taller = %s
    """, (id_taller,))

    taller = cursor.fetchone()

    if not taller:
        cursor.close()
        conexion.close()
        return "Taller no encontrado"

    cursor.execute("""
        SELECT
            id_plan,
            nombre,
            tipo,
            cantidad_clases,
            precio
        FROM planes
        WHERE id_taller = %s
        ORDER BY cantidad_clases
    """, (id_taller,))

    planes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "planes_taller.html",
        taller=taller,
        planes=planes
    )

@app.route("/taller/<int:id_taller>/plan/<int:id_plan>/confirmar")
def confirmar_inscripcion(id_taller, id_plan):

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.id_taller,
            t.nombre AS taller,
            t.horario,
            p.id_plan,
            p.nombre AS plan,
            p.tipo,
            p.cantidad_clases,
            p.precio
        FROM planes p

        INNER JOIN talleres t
            ON p.id_taller = t.id_taller

        WHERE p.id_plan = %s
        AND t.id_taller = %s        # comprueba que el plan realmente pertenezca al taller
    """, (id_plan, id_taller))

    datos = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not datos:
        return "El plan seleccionado no corresponde a este taller"

    return render_template(
        "confirmar_inscripcion.html",
        datos=datos
    )


@app.route("/taller/<int:id_taller>/plan/<int:id_plan>/inscribir", methods=["POST"])
def inscribir_taller(id_taller, id_plan):

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

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

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # 1. Buscar al alumno que inició sesión
        cursor.execute("""
            SELECT id_alumno
            FROM alumnos
            WHERE id_usuario = %s
        """, (id_usuario,))

        alumno = cursor.fetchone()

        if not alumno:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Alumno no encontrado",
                mensaje="No se pudo encontrar tu registro de alumno.",
                texto_boton="Volver al inicio",
                destino=url_for("inicio")
            )

        id_alumno = alumno["id_alumno"]


        # 2. Comprobar que el plan pertenece al taller
        cursor.execute("""
            SELECT
                id_plan,
                id_taller,
                cantidad_clases,
                precio
            FROM planes
            WHERE id_plan = %s
            AND id_taller = %s
        """, (id_plan, id_taller))

        plan = cursor.fetchone()

        if not plan:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Plan no válido",
                mensaje="El plan seleccionado no corresponde a este taller.",
                texto_boton="Volver a talleres",
                destino=url_for("talleres_disponibles")
            )


        # 3. Comprobar si ya tiene una inscripción activa
        cursor.execute("""
            SELECT id_inscripcion
            FROM inscripciones
            WHERE id_alumno = %s
            AND id_taller = %s
            AND estado = 'activa'
        """, (id_alumno, id_taller))

        inscripcion_existente = cursor.fetchone()

        if inscripcion_existente:
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Ya estás inscrito",
                mensaje="Ya tienes una inscripción activa en este taller.",
                texto_boton="Ir a mis talleres",
                destino=url_for("mis_talleres")
            )


        # 4. Crear la inscripción
        cursor.execute("""
            INSERT INTO inscripciones (
                id_alumno,
                id_taller,
                fecha_inscripcion,
                estado,
                id_plan,
                fecha_inicio,
                fecha_vencimiento,
                clases_contratadas,
                precio_acordado
            )
            VALUES (
                %s,
                %s,
                CURDATE(),
                'activa',
                %s,
                CURDATE(),
                DATE_ADD(CURDATE(), INTERVAL 1 MONTH),
                %s,
                %s
            )
        """, (
            id_alumno,
            id_taller,
            id_plan,
            plan["cantidad_clases"],
            plan["precio"]
        ))

        conexion.commit()

        return render_template(
            "mensaje.html",
            tipo="exito",
            titulo="Inscripción realizada",
            mensaje="Tu inscripción fue realizada correctamente.",
            texto_boton="Ir a mis talleres",
            destino=url_for("mis_talleres")
        )

    except Exception as error:

        conexion.rollback()

        print("Error al realizar inscripción:", error)

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No pudimos realizar la inscripción",
            mensaje="Ocurrió un error al procesar tu inscripción.",
            texto_boton="Volver a talleres",
            destino=url_for("talleres_disponibles")
        )

    finally:

        cursor.close()
        conexion.close()


@app.route("/mis_talleres")
def mis_talleres():

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

    if session.get("rol") != "alumno":
        return "Acceso no autorizado"

    id_usuario = session["id_usuario"]

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            i.id_inscripcion,
            i.estado,
            i.fecha_inicio,
            i.fecha_vencimiento,
            i.clases_contratadas,
            i.precio_acordado,

            t.id_taller,
            t.nombre AS taller,
            t.horario,

            p.nombre AS plan

        FROM inscripciones i

        INNER JOIN alumnos a
            ON i.id_alumno = a.id_alumno

        INNER JOIN talleres t
            ON i.id_taller = t.id_taller

        INNER JOIN planes p
            ON i.id_plan = p.id_plan

        WHERE a.id_usuario = %s
        AND i.estado = 'activa'

        ORDER BY t.nombre
    """, (id_usuario,))

    inscripciones = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "mis_talleres.html",
        inscripciones=inscripciones
    )

@app.route("/inscripcion/<int:id_inscripcion>/clases")
def clases_disponibles_alumno(id_inscripcion):

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

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

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    # Verificar que la inscripción pertenezca al alumno conectado
    cursor.execute("""
        SELECT
            i.id_inscripcion,
            i.id_taller,
            i.estado,
            i.clases_contratadas,
            t.nombre AS taller

        FROM inscripciones i

        INNER JOIN alumnos a
            ON i.id_alumno = a.id_alumno

        INNER JOIN talleres t
            ON i.id_taller = t.id_taller

        WHERE i.id_inscripcion = %s
        AND a.id_usuario = %s
        AND i.estado = 'activa'
    """, (id_inscripcion, id_usuario))

    inscripcion = cursor.fetchone()

    if not inscripcion:
        cursor.close()
        conexion.close()
        return "Inscripción no encontrada o acceso no autorizado"

    id_taller = inscripcion["id_taller"]

    # Contar cuántas clases ha reservado esta inscripción
    cursor.execute("""
        SELECT COUNT(*) AS usadas
        FROM reservas_clase
        WHERE id_inscripcion = %s
        AND consume_clase = 1
    """, (id_inscripcion,))

    resultado = cursor.fetchone()

    clases_usadas = resultado["usadas"]

    clases_disponibles = (
        inscripcion["clases_contratadas"] - clases_usadas
    )

    # Obtener las clases del taller,
    # contar reservas activas
    # y verificar si el alumno ya reservó cada clase
    cursor.execute("""
        SELECT
            c.id_clase,
            c.fecha,
            c.hora_inicio,
            c.hora_fin,
            c.cupo_maximo,
            c.estado,

            (
                SELECT COUNT(*)
                FROM reservas_clase r
                WHERE r.id_clase = c.id_clase
                AND r.estado = 'reservada'
            ) AS reservados,

            (
                SELECT r2.id_reserva
                FROM reservas_clase r2
                WHERE r2.id_clase = c.id_clase
                AND r2.id_inscripcion = %s
                AND r2.estado = 'reservada'
                LIMIT 1
            ) AS mi_reserva

        FROM clases c

        WHERE c.id_taller = %s
        AND c.estado = 'programada'
        -- solo muestra clases futuras 
        AND TIMESTAMP(c.fecha, c.hora_inicio) > NOW()  
        

        ORDER BY c.fecha, c.hora_inicio
    """, (id_inscripcion, id_taller))

    clases = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "clases_disponibles_alumno.html",
        inscripcion=inscripcion,
        clases=clases,
        clases_usadas=clases_usadas,
        clases_disponibles=clases_disponibles
    )


@app.route(
    "/inscripcion/<int:id_inscripcion>/clase/<int:id_clase>/reservar",
    methods=["POST"]
)
def reservar_clase(id_inscripcion, id_clase):

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

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

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # 1. Comprobar que la inscripción pertenece al alumno
        cursor.execute("""
            SELECT
                i.id_inscripcion,
                i.id_taller,
                i.estado,
                i.clases_contratadas

            FROM inscripciones i

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            WHERE i.id_inscripcion = %s
            AND a.id_usuario = %s
            AND i.estado = 'activa'
        """, (id_inscripcion, id_usuario))

        inscripcion = cursor.fetchone()

        if not inscripcion:
            return render_template(
                "mensaje.html",
                tipo="error",
                titulo="Inscripción no válida",
                mensaje="La inscripción no existe o no pertenece a tu cuenta.",
                texto_boton="Volver a mis talleres",
                destino=url_for("mis_talleres")
            )


        # 2. Comprobar cuántas clases del plan ya fueron utilizadas
        cursor.execute("""
            SELECT COUNT(*) AS usadas

            FROM reservas_clase

            WHERE id_inscripcion = %s
            AND consume_clase = 1
        """, (id_inscripcion,))

        resultado = cursor.fetchone()

        clases_usadas = resultado["usadas"]

        if clases_usadas >= inscripcion["clases_contratadas"]:
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Sin clases disponibles",
                mensaje="Ya utilizaste todas las clases disponibles de tu plan.",
                texto_boton="Volver a mis clases",
                destino=url_for(
                    "clases_disponibles_alumno",
                    id_inscripcion=id_inscripcion
                )
            )


        # 3. Comprobar que la clase pertenece al mismo taller
        #    y que todavía no haya comenzado
        cursor.execute("""
            SELECT
                id_clase,
                id_taller,
                fecha,
                hora_inicio,
                hora_fin,
                cupo_maximo,
                estado

            FROM clases

            WHERE id_clase = %s
            AND id_taller = %s
            AND estado = 'programada'
            AND TIMESTAMP(fecha, hora_inicio) > NOW()
        """, (
            id_clase,
            inscripcion["id_taller"]
        ))

        clase = cursor.fetchone()

        if not clase:
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Clase no disponible",
                mensaje="La clase ya comenzó, pasó de fecha o dejó de estar disponible.",
                texto_boton="Volver a las clases",
                destino=url_for(
                    "clases_disponibles_alumno",
                    id_inscripcion=id_inscripcion
                )
            )


        # 4. Comprobar si ya existe una reserva activa
        cursor.execute("""
            SELECT id_reserva

            FROM reservas_clase

            WHERE id_inscripcion = %s
            AND id_clase = %s
            AND estado = 'reservada'
        """, (
            id_inscripcion,
            id_clase
        ))

        reserva_existente = cursor.fetchone()

        if reserva_existente:
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Clase ya reservada",
                mensaje="Ya tienes una reserva activa para esta clase.",
                texto_boton="Volver a las clases",
                destino=url_for(
                    "clases_disponibles_alumno",
                    id_inscripcion=id_inscripcion
                )
            )


        # 5. Comprobar los cupos ocupados
        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM reservas_clase

            WHERE id_clase = %s
            AND estado = 'reservada'
        """, (id_clase,))

        resultado = cursor.fetchone()

        reservados = resultado["total"]

        if reservados >= clase["cupo_maximo"]:
            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Clase completa",
                mensaje="Esta clase ya alcanzó su cupo máximo.",
                texto_boton="Volver a las clases",
                destino=url_for(
                    "clases_disponibles_alumno",
                    id_inscripcion=id_inscripcion
                )
            )


        # 6. Guardar la reserva
        #    Se vuelve a comprobar que la clase siga siendo futura
        cursor.execute("""
            INSERT INTO reservas_clase (
                id_inscripcion,
                id_clase,
                estado,
                consume_clase
            )

            SELECT
                %s,
                id_clase,
                'reservada',
                1

            FROM clases

            WHERE id_clase = %s
            AND estado = 'programada'
            AND TIMESTAMP(fecha, hora_inicio) > NOW()
        """, (
            id_inscripcion,
            id_clase
        ))


        # 7. Verificar que realmente se haya insertado
        if cursor.rowcount != 1:

            conexion.rollback()

            return render_template(
                "mensaje.html",
                tipo="aviso",
                titulo="Clase no disponible",
                mensaje="La clase dejó de estar disponible antes de completar la reserva.",
                texto_boton="Volver a las clases",
                destino=url_for(
                    "clases_disponibles_alumno",
                    id_inscripcion=id_inscripcion
                )
            )


        conexion.commit()

        return redirect(url_for(
            "clases_disponibles_alumno",
            id_inscripcion=id_inscripcion
        ))


    except Exception as error:

        conexion.rollback()

        print("Error al reservar clase:", error)

        return render_template(
            "mensaje.html",
            tipo="error",
            titulo="No pudimos realizar la reserva",
            mensaje="Ocurrió un error al intentar reservar la clase.",
            texto_boton="Volver a mis talleres",
            destino=url_for("mis_talleres")
        )


    finally:

        cursor.close()
        conexion.close()
#* ------------------------------------------------------------- #
@app.route("/reserva/<int:id_reserva>/cancelar", methods=["POST"])
def cancelar_reserva(id_reserva):

    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))

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

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:
        # Verificar que la reserva pertenezca al alumno conectado
        cursor.execute("""
            SELECT
                r.id_reserva,
                r.id_inscripcion,
                r.estado
            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON r.id_inscripcion = i.id_inscripcion

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            WHERE r.id_reserva = %s
            AND a.id_usuario = %s
        """, (id_reserva, id_usuario))

        reserva = cursor.fetchone()

        if not reserva:
            return render_template(
        "mensaje.html",
        tipo="error",
        titulo="Reserva no encontrada",
        mensaje="No encontramos esta reserva o no tienes acceso a ella.",
        texto_boton="Volver a mis talleres",
        destino=url_for("mis_talleres")
    )

        if reserva["estado"] != "reservada":
            return render_template(
        "mensaje.html",
        tipo="aviso",
        titulo="Reserva no activa",
        mensaje="Esta reserva ya no se encuentra activa.",
        texto_boton="Volver a mis talleres",
        destino=url_for("mis_talleres")
    )

        # Cancelar sin borrar: recuperar la clase solo con dos horas o más.
        cursor.execute("""
            UPDATE reservas_clase r
            INNER JOIN clases c ON c.id_clase = r.id_clase
            SET
                r.estado = 'cancelada',
                r.fecha_cancelacion = NOW(),
                r.consume_clase = CASE
                    WHEN TIMESTAMP(c.fecha, c.hora_inicio)
                         >= DATE_ADD(NOW(), INTERVAL 2 HOUR)
                    THEN 0
                    ELSE 1
                END
            WHERE r.id_reserva = %s
              AND r.estado = 'reservada'
        """, (id_reserva,))

        conexion.commit()

        return redirect(url_for(
            "clases_disponibles_alumno",
            id_inscripcion=reserva["id_inscripcion"]
        ))

    except Exception as error:
        conexion.rollback()
        print("Error al cancelar reserva:", error)
        return render_template(
    "mensaje.html",
    tipo="error",
    titulo="No pudimos cancelar la reserva",
    mensaje="Ocurrió un error al intentar cancelar la clase.",
    texto_boton="Volver a mis talleres",
    destino=url_for("mis_talleres")
)

    finally:
        cursor.close()
        conexion.close()

# =========================
# API TALLERES  - desde línea 1249 hasta 1792
# =========================

@app.route("/api/talleres", methods=["GET"])
def api_talleres():

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_taller,
                nombre,
                descripcion,
                horario,
                cupo_maximo
            FROM talleres
            ORDER BY id_taller
        """)

        talleres = cursor.fetchall()

        return jsonify({"talleres": talleres}), 200


    except mysql.connector.Error:

        app.logger.exception("Error al consultar los talleres")

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudieron consultar los talleres."
            }
        }), 500


    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()



@app.route("/api/talleres/<int:id_taller>", methods=["GET"])
def api_taller_detalle(id_taller):

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_taller,
                nombre,
                descripcion,
                horario,
                cupo_maximo
            FROM talleres
            WHERE id_taller = %s
        """, (id_taller,))

        taller = cursor.fetchone()

        if not taller:
            return jsonify({
                "error": {
                    "codigo": "taller_no_encontrado",
                    "mensaje": "El taller solicitado no existe."
                }
            }), 404

        return jsonify({
            "taller": taller
        }), 200

    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar el detalle del taller"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudo consultar el taller."
            }
        }), 500

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()




@app.route("/api/talleres/<int:id_taller>/clases", methods=["GET"])
def api_clases_taller(id_taller):

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que el taller exista
        cursor.execute("""
            SELECT
                id_taller,
                nombre
            FROM talleres
            WHERE id_taller = %s
        """, (id_taller,))

        taller = cursor.fetchone()

        if not taller:
            return jsonify({
                "error": {
                    "codigo": "taller_no_encontrado",
                    "mensaje": "El taller solicitado no existe."
                }
            }), 404

        # Obtener las clases del taller
        cursor.execute("""
            SELECT
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.cupo_maximo,
                c.estado,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r
                    WHERE r.id_clase = c.id_clase
                    AND r.estado = 'reservada'
                ) AS alumnos_reservados

            FROM clases c

            WHERE c.id_taller = %s
            AND c.estado = 'programada'
            AND TIMESTAMP(c.fecha, c.hora_inicio) > NOW()  -- solo clases futuras

            ORDER BY c.fecha, c.hora_inicio
        """, (id_taller,))

        clases = cursor.fetchall()

        # Convertir tipos de MySQL a valores compatibles con JSON
        for clase in clases:

            if clase["fecha"] is not None:
                clase["fecha"] = str(clase["fecha"])

            if clase["hora_inicio"] is not None:
                clase["hora_inicio"] = str(clase["hora_inicio"])

            if clase["hora_fin"] is not None:
                clase["hora_fin"] = str(clase["hora_fin"])

        return jsonify({
            "taller": {
                "id_taller": taller["id_taller"],
                "nombre": taller["nombre"]
            },
            "total_clases": len(clases),
            "clases": clases
        }), 200

    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar las clases del taller"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudieron consultar las clases."
            }
        }), 500

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


@app.route("/api/estadisticas/resumen", methods=["GET"])
def api_estadisticas_resumen():

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        # Total de alumnos
        cursor.execute("""
            SELECT COUNT(*) AS total_alumnos
            FROM alumnos
        """)
        total_alumnos = cursor.fetchone()["total_alumnos"]

        # Total de talleres
        cursor.execute("""
            SELECT COUNT(*) AS total_talleres
            FROM talleres
        """)
        total_talleres = cursor.fetchone()["total_talleres"]

        # Total de clases
        cursor.execute("""
            SELECT COUNT(*) AS total_clases
            FROM clases
        """)
        total_clases = cursor.fetchone()["total_clases"]

        # Reservas activas
        cursor.execute("""
            SELECT COUNT(*) AS reservas_activas
            FROM reservas_clase
            WHERE estado = 'reservada'
        """)
        reservas_activas = cursor.fetchone()["reservas_activas"]

        # Reservas canceladas
        cursor.execute("""
            SELECT COUNT(*) AS reservas_canceladas
            FROM reservas_clase
            WHERE estado = 'cancelada'
        """)
        reservas_canceladas = cursor.fetchone()["reservas_canceladas"]

        return jsonify({
            "estadisticas": {
                "total_alumnos": total_alumnos,
                "total_talleres": total_talleres,
                "total_clases": total_clases,
                "reservas_activas": reservas_activas,
                "reservas_canceladas": reservas_canceladas
            }
        }), 200

    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar estadísticas"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudieron obtener las estadísticas."
            }
        }), 500

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()




@app.route("/api/estadisticas/talleres", methods=["GET"])
def api_estadisticas_talleres():

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre AS taller,
                COUNT(r.id_reserva) AS total_reservas,

                SUM(
                    CASE
                        WHEN r.estado = 'reservada' THEN 1
                        ELSE 0
                    END
                ) AS reservas_activas,

                SUM(
                    CASE
                        WHEN r.estado = 'cancelada' THEN 1
                        ELSE 0
                    END
                ) AS reservas_canceladas

            FROM talleres t

            LEFT JOIN clases c
                ON t.id_taller = c.id_taller

            LEFT JOIN reservas_clase r
                ON c.id_clase = r.id_clase

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY total_reservas DESC
        """)

        talleres = cursor.fetchall()

        return jsonify({
            "total_talleres": len(talleres),
            "talleres": talleres
        }), 200

    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar estadísticas por taller"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudieron obtener las estadísticas por taller."
            }
        }), 500

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


@app.route("/api/estadisticas/ocupacion-talleres", methods=["GET"])
def api_ocupacion_talleres():

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre AS taller,

                COUNT(c.id_clase) AS total_clases,

                COALESCE(SUM(c.cupo_maximo), 0) AS cupos_totales,

                COALESCE(SUM(c.reservas_activas), 0) AS reservas_activas

            FROM talleres t

            LEFT JOIN (
                SELECT
                    cl.id_clase,
                    cl.id_taller,
                    cl.cupo_maximo,

                    COUNT(
                        CASE
                            WHEN r.estado = 'reservada'
                            THEN r.id_reserva
                        END
                    ) AS reservas_activas

                FROM clases cl

                LEFT JOIN reservas_clase r
                    ON cl.id_clase = r.id_clase

                GROUP BY
                    cl.id_clase,
                    cl.id_taller,
                    cl.cupo_maximo
            ) c
                ON t.id_taller = c.id_taller

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY
                t.nombre
        """)

        talleres = cursor.fetchall()

        for taller in talleres:

            cupos_totales = taller["cupos_totales"]
            reservas_activas = taller["reservas_activas"]

            if cupos_totales > 0:
                ocupacion = (
                    reservas_activas / cupos_totales
                ) * 100
            else:
                ocupacion = 0

            taller["porcentaje_ocupacion"] = round(ocupacion, 2)

        return jsonify({
            "total_talleres": len(talleres),
            "talleres": talleres
        }), 200

    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar ocupación de talleres"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudo obtener la ocupación de los talleres."
            }
        }), 500

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()



@app.route("/api/estadisticas/demanda-talleres", methods=["GET"])
def api_demanda_talleres():

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre AS taller,

                COUNT(
                    CASE
                        WHEN r.estado = 'reservada'
                        THEN r.id_reserva
                    END
                ) AS reservas_activas,

                COUNT(
                    CASE
                        WHEN r.estado = 'cancelada'
                        THEN r.id_reserva
                    END
                ) AS reservas_canceladas,

                COUNT(r.id_reserva) AS total_reservas

            FROM talleres t

            LEFT JOIN clases c
                ON t.id_taller = c.id_taller

            LEFT JOIN reservas_clase r
                ON c.id_clase = r.id_clase

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY
                reservas_activas DESC,
                total_reservas DESC
        """)

        talleres = cursor.fetchall()

        return jsonify({
            "total_talleres": len(talleres),
            "ranking_demanda": talleres
        }), 200

    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar demanda de talleres"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudo obtener la demanda de los talleres."
            }
        }), 500

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


# =========================
# API TALLERES FINAL CÓDIGO 
# =========================



# =========================
# ANALISIS DE DATOS  
# =========================



@app.route("/analisis")
def analisis():

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        # -------------------------------------------------
        # TOTAL DE ALUMNOS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM alumnos
        """)

        total_alumnos = cursor.fetchone()["total"]


        # -------------------------------------------------
        # TOTAL DE TALLERES
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM talleres
        """)

        total_talleres = cursor.fetchone()["total"]


        # -------------------------------------------------
        # RESERVAS ACTIVAS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas_clase
            WHERE estado = 'reservada'
        """)

        reservas_activas = cursor.fetchone()["total"]


        # -------------------------------------------------
        # RESERVAS CANCELADAS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas_clase
            WHERE estado = 'cancelada'
        """)

        reservas_canceladas = cursor.fetchone()["total"]


        # -------------------------------------------------
        # TASA DE CANCELACIÓN
        # -------------------------------------------------

        total_reservas = (
            reservas_activas +
            reservas_canceladas
        )

        if total_reservas > 0:

            tasa_cancelacion = round(
                (reservas_canceladas / total_reservas) * 100,
                1
            )

        else:

            tasa_cancelacion = 0


        # -------------------------------------------------
        # DEMANDA POR TALLER
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre AS taller,

                COUNT(
                    CASE
                        WHEN r.estado = 'reservada'
                        THEN r.id_reserva
                    END
                ) AS reservas

            FROM talleres t

            LEFT JOIN clases c
                ON t.id_taller = c.id_taller

            LEFT JOIN reservas_clase r
                ON c.id_clase = r.id_clase

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY
                reservas DESC,
                t.nombre
        """)

        talleres = cursor.fetchall()


        # -------------------------------------------------
        # TALLER MÁS DEMANDADO
        # -------------------------------------------------

        if talleres and talleres[0]["reservas"] > 0:

            taller_mas_demandado = talleres[0]["taller"]
            reservas_taller_mas_demandado = talleres[0]["reservas"]

        else:

            taller_mas_demandado = "Sin reservas"
            reservas_taller_mas_demandado = 0


        # -------------------------------------------------
        # ENVIAR DATOS A HTML
        # -------------------------------------------------

        return render_template(
            "analisis.html",

            total_alumnos=total_alumnos,

            total_talleres=total_talleres,

            reservas_activas=reservas_activas,

            reservas_canceladas=reservas_canceladas,

            tasa_cancelacion=tasa_cancelacion,

            taller_mas_demandado=taller_mas_demandado,

            reservas_taller_mas_demandado=
                reservas_taller_mas_demandado,

            talleres=talleres
        )


    except mysql.connector.Error:

        app.logger.exception(
            "Error al cargar el panel de análisis"
        )

        return "No se pudo cargar el panel de análisis"


    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


@app.route("/api/estadisticas/reservas-historicas", methods=["GET"])
def api_reservas_historicas():

    conexion = None
    cursor = None

    try:

        periodo = request.args.get("periodo", "mes")

        if periodo == "dia":
            formato_fecha = "%Y-%m-%d"

        elif periodo == "mes":
            formato_fecha = "%Y-%m"

        elif periodo == "anio":
            formato_fecha = "%Y"

        else:

            return jsonify({
                "error": {
                    "codigo": "periodo_invalido",
                    "mensaje": "El periodo debe ser dia, mes o anio."
                }
            }), 400


        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)


        consulta = f"""
            SELECT

                DATE_FORMAT(
                    fecha_reserva,
                    '{formato_fecha}'
                ) AS periodo,

                COUNT(*) AS total_reservas,

                SUM(
                    CASE
                        WHEN estado = 'reservada'
                        THEN 1
                        ELSE 0
                    END
                ) AS reservas_activas,

                SUM(
                    CASE
                        WHEN estado = 'cancelada'
                        THEN 1
                        ELSE 0
                    END
                ) AS reservas_canceladas

            FROM reservas_clase

            GROUP BY
                DATE_FORMAT(
                    fecha_reserva,
                    '{formato_fecha}'
                )

            ORDER BY periodo
        """

        cursor.execute(consulta)

        historial = cursor.fetchall()


        return jsonify({
            "periodo": periodo,
            "total_periodos": len(historial),
            "historial": historial
        }), 200


    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar historial de reservas"
        )

        return jsonify({
            "error": {
                "codigo": "error_base_datos",
                "mensaje": "No se pudo consultar el historial de reservas."
            }
        }), 500


    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()






# FUNCIONES NUEVAS PARA ESTADISTICAS DEL ALUMNO
@app.route("/mis_estadisticas")
def mis_estadisticas():
    if "id_usuario" not in session:
        return redirect(url_for("login_alumno"))
    if session.get("rol") != "alumno":
        return "Acceso no autorizado", 403
    return render_template("mis_estadisticas.html")


@app.route("/api/alumno/estadisticas", methods=["GET"])
def api_alumno_estadisticas():
    if "id_usuario" not in session:
        return jsonify({"error": {"mensaje": "Inicia sesión para consultar tus estadísticas."}}), 401
    if session.get("rol") != "alumno":
        return jsonify({"error": {"mensaje": "Acceso exclusivo para alumnos."}}), 403

    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_alumno FROM alumnos WHERE id_usuario = %s
        """, (session["id_usuario"],))
        alumno = cursor.fetchone()
        if not alumno:
            return jsonify({"error": {"mensaje": "No se encontró tu perfil de alumno."}}), 404

        # Planes activos cuya vigencia incluye el día actual.
        cursor.execute("""
            SELECT COUNT(DISTINCT id_taller) AS talleres_vigentes,
                COALESCE(SUM(clases_contratadas), 0) AS clases_contratadas_vigentes
            FROM inscripciones
            WHERE id_alumno = %s AND estado = 'activa'
            AND fecha_inicio <= CURDATE()
            AND fecha_vencimiento >= CURDATE()
        """, (alumno["id_alumno"],))
        planes = cursor.fetchone()

        # Historial personal: no se recibe un id de alumno del navegador.
        cursor.execute("""
            SELECT COUNT(*) AS total_reservas,
                COALESCE(SUM(CASE WHEN r.estado = 'cancelada' THEN 1 ELSE 0 END), 0) AS reservas_canceladas,
                COALESCE(SUM(CASE WHEN r.estado = 'reservada'
                    AND c.estado = 'programada'
                    AND TIMESTAMP(c.fecha, c.hora_inicio) > NOW()
                    THEN 1 ELSE 0 END), 0) AS reservas_proximas
            FROM reservas_clase r
            INNER JOIN inscripciones i ON i.id_inscripcion = r.id_inscripcion
            INNER JOIN clases c ON c.id_clase = r.id_clase
            WHERE i.id_alumno = %s
        """, (alumno["id_alumno"],))
        reservas = cursor.fetchone()

        cursor.execute("""
            SELECT t.nombre AS taller, COUNT(*) AS reservas
            FROM reservas_clase r
            INNER JOIN inscripciones i ON i.id_inscripcion = r.id_inscripcion
            INNER JOIN clases c ON c.id_clase = r.id_clase
            INNER JOIN talleres t ON t.id_taller = c.id_taller
            WHERE i.id_alumno = %s AND r.estado = 'reservada'
            AND c.estado <> 'cancelada'
            GROUP BY t.id_taller, t.nombre
            ORDER BY reservas DESC, t.nombre
        """, (alumno["id_alumno"],))
        talleres = cursor.fetchall()

        respuesta = jsonify({
            "estadisticas": {
                "talleres_vigentes": int(planes["talleres_vigentes"]),
                "clases_contratadas_vigentes": int(planes["clases_contratadas_vigentes"]),
                "reservas_proximas": int(reservas["reservas_proximas"]),
                "total_reservas": int(reservas["total_reservas"]),
                "reservas_canceladas": int(reservas["reservas_canceladas"]),
                "porcentaje_asistencia": None,
                "porcentaje_inasistencia": None
            },
            "mis_talleres_mas_reservados": [
                {"taller": t["taller"], "reservas": int(t["reservas"])} for t in talleres
            ]
        })
        respuesta.headers["Cache-Control"] = "no-store"
        return respuesta, 200
    except mysql.connector.Error:
        app.logger.exception("Error al consultar estadísticas del alumno")
        return jsonify({"error": {"mensaje": "No se pudieron cargar tus estadísticas. Intenta nuevamente."}}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()



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



@app.route("/api/profesor/estadisticas", methods=["GET"])
def api_profesor_estadisticas():

    if "id_usuario" not in session:

        return jsonify({
            "error": {
                "mensaje": "Inicia sesión para consultar tus estadísticas."
            }
        }), 401


    if session.get("rol") != "profesor":

        return jsonify({
            "error": {
                "mensaje": "Acceso exclusivo para profesores."
            }
        }), 403


    conexion = None
    cursor = None


    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)


        # ==========================================
        # 1. OBTENER PROFESOR CONECTADO
        # ==========================================

        cursor.execute("""
            SELECT
                id_profesor,
                nombre,
                apellido

            FROM profesores

            WHERE id_usuario = %s
        """, (session["id_usuario"],))

        profesor = cursor.fetchone()


        if not profesor:

            return jsonify({
                "error": {
                    "mensaje": "No se encontró tu perfil de profesor."
                }
            }), 404


        id_profesor = profesor["id_profesor"]


        # ==========================================
        # 2. TALLERES ASIGNADOS
        # ==========================================

        cursor.execute("""
            SELECT COUNT(DISTINCT id_taller) AS total

            FROM taller_profesor

            WHERE id_profesor = %s
        """, (id_profesor,))

        talleres_asignados = cursor.fetchone()["total"]


        # ==========================================
        # 3. ALUMNOS ACTIVOS
        # ==========================================

        cursor.execute("""
            SELECT COUNT(DISTINCT i.id_alumno) AS total

            FROM inscripciones i

            INNER JOIN taller_profesor tp
                ON i.id_taller = tp.id_taller

            WHERE tp.id_profesor = %s
            AND i.estado = 'activa'
        """, (id_profesor,))

        alumnos_activos = cursor.fetchone()["total"]


        # ==========================================
        # 4. PRÓXIMAS CLASES
        # ==========================================

        cursor.execute("""
            SELECT COUNT(DISTINCT c.id_clase) AS total

            FROM clases c

            INNER JOIN taller_profesor tp
                ON c.id_taller = tp.id_taller

            WHERE tp.id_profesor = %s
            AND c.estado = 'programada'
            AND TIMESTAMP(c.fecha, c.hora_inicio) > NOW()
        """, (id_profesor,))

        proximas_clases = cursor.fetchone()["total"]


        # ==========================================
        # 5. RESERVAS ACTIVAS Y CANCELADAS
        # ==========================================

        cursor.execute("""
            SELECT

                COUNT(
                    CASE
                        WHEN r.estado = 'reservada'
                        THEN r.id_reserva
                    END
                ) AS reservas_activas,

                COUNT(
                    CASE
                        WHEN r.estado = 'cancelada'
                        THEN r.id_reserva
                    END
                ) AS reservas_canceladas

            FROM reservas_clase r

            INNER JOIN clases c
                ON r.id_clase = c.id_clase

            INNER JOIN taller_profesor tp
                ON c.id_taller = tp.id_taller

            WHERE tp.id_profesor = %s
        """, (id_profesor,))

        reservas = cursor.fetchone()


        # ==========================================
        # 6. ESTADÍSTICAS POR TALLER
        # ==========================================

        cursor.execute("""
            SELECT

                t.id_taller,

                t.nombre AS taller,

                COUNT(DISTINCT c.id_clase) AS total_clases,

                COALESCE(
                    SUM(c.cupo_maximo),
                    0
                ) AS cupos_totales,

                COUNT(
                    CASE
                        WHEN r.estado = 'reservada'
                        THEN r.id_reserva
                    END
                ) AS reservas_activas,

                COUNT(
                    CASE
                        WHEN r.estado = 'cancelada'
                        THEN r.id_reserva
                    END
                ) AS reservas_canceladas

            FROM talleres t

            INNER JOIN taller_profesor tp
                ON t.id_taller = tp.id_taller

            LEFT JOIN clases c
                ON t.id_taller = c.id_taller

            LEFT JOIN reservas_clase r
                ON c.id_clase = r.id_clase

            WHERE tp.id_profesor = %s

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY
                reservas_activas DESC,
                t.nombre
        """, (id_profesor,))

        talleres = cursor.fetchall()


        # ==========================================
        # 7. CALCULAR OCUPACIÓN
        # ==========================================

        for taller in talleres:

            cupos = int(
                taller["cupos_totales"] or 0
            )

            activas = int(
                taller["reservas_activas"] or 0
            )


            if cupos > 0:

                porcentaje = (
                    activas / cupos
                ) * 100

            else:

                porcentaje = 0


            taller["cupos_totales"] = cupos

            taller["reservas_activas"] = activas

            taller["reservas_canceladas"] = int(
                taller["reservas_canceladas"] or 0
            )

            taller["total_clases"] = int(
                taller["total_clases"] or 0
            )

            taller["porcentaje_ocupacion"] = round(
                porcentaje,
                2
            )


        # ==========================================
        # 8. OCUPACIÓN PROMEDIO
        # ==========================================

        if talleres:

            ocupacion_promedio = sum(
                taller["porcentaje_ocupacion"]
                for taller in talleres
            ) / len(talleres)

        else:

            ocupacion_promedio = 0


        # ==========================================
        # 9. RESPUESTA JSON
        # ==========================================

        respuesta = jsonify({

            "profesor": {
                "nombre": profesor["nombre"],
                "apellido": profesor["apellido"]
            },

            "estadisticas": {

                "talleres_asignados":
                    int(talleres_asignados),

                "alumnos_activos":
                    int(alumnos_activos),

                "proximas_clases":
                    int(proximas_clases),

                "reservas_activas":
                    int(reservas["reservas_activas"] or 0),

                "reservas_canceladas":
                    int(reservas["reservas_canceladas"] or 0),

                "ocupacion_promedio":
                    round(ocupacion_promedio, 2)
            },

            "talleres": talleres

        })


        respuesta.headers["Cache-Control"] = "no-store"

        return respuesta, 200


    except mysql.connector.Error:

        app.logger.exception(
            "Error al consultar estadísticas del profesor"
        )

        return jsonify({
            "error": {
                "mensaje":
                    "No se pudieron cargar tus estadísticas. "
                    "Intenta nuevamente."
            }
        }), 500


    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()





if __name__ == "__main__":
    app.run(debug=True)